# conversation_module/lex_handler.py
import boto3
import os
import re

class LexHandler:
    def __init__(self):
        # Initialize the Lex V2 runtime client
        self.lex_client = boto3.client('lexv2-runtime', region_name=os.getenv('AWS_DEFAULT_REGION'))
        self.bookList = ['harry potter', 'journey to the west', 'a brief history of time']

    def matric_local_validation(self, matricNum, session_state, messages):
        """
        Validates the matriculation number format using regex.
        Returns a Lex response based on the validation result.
        """
        # Trim leading/trailing spaces and convert to uppercase
        text = matricNum.strip().lower() # if matricNum else ""

        # Case-insensitive matching (A1234567Z, UT9876543X, etc.)
        pattern = re.compile(r'^(ut|ht|a|u)[0-9]{7}[a-z]$', re.IGNORECASE)

        print(f"Input: '{text}'")
        print(f"Regex Pattern: {pattern.pattern}")
        print(f'session state is {session_state}')
        print(f'messages are {messages}')

        if pattern.match(text):
            print(f'format of {text} is a match.')
            temp = {'sessionState':{'dialogAction':session_state['dialogAction'],'intent':session_state['intent']}}
            temp['sessionState']['intent']['slots']['BookName'], temp['sessionState']['intent']['slots']['StuEmail']= {},{}
            temp['messages'] = messages
            # print(f'success temp session state is {temp}') 
            return temp
            
        else:
            print(f'format of {text} is no match.')
            temp = {'sessionState': {'dialogAction':session_state['dialogAction'],'intent':session_state['intent']}}
            temp['sessionState']['dialogAction']['slotToElicit'] ='MatricNum'
            temp['messages'] = [{}]
            temp['messages'][0]['content'] = 'Invalid matriculation number. Please enter a valid one e.g. A0012345Z.'
            temp['messages'][0]['contentType'] = 'PlainText'
            temp['sessionState']['intent']['slots']= {'BookName':{}, 'MatricNum':{}, 'StuEmail':{}}
            # print(f'no match temp session state is {temp}') 
            return temp


    def book_local_validation(self, bookName, session_state, messages):
        
        # Trim leading/trailing spaces and convert to uppercase
        text = bookName.strip().lower()

        print(f"Input: '{text}'")
        print(f'session state is {session_state}')
        print(f'messages are {messages}')

        if text in self.bookList:
            print(f'book [{text}] is found in the book list.')
            temp = {'sessionState':{'dialogAction':session_state['dialogAction'],'intent':session_state['intent']}}
            temp['sessionState']['intent']['slots']['StuEmail']= {}
            temp['messages'] = messages
            # print(f'success temp session state is {temp}') 
            return temp
            
        else:
            print(f'book [{text}] is not found in the book list.')
            temp = {'sessionState': {'dialogAction':session_state['dialogAction'],'intent':session_state['intent']}}
            temp['sessionState']['dialogAction']['slotToElicit'] ='BookName'
            temp['messages'] = [{}]
            temp['messages'][0]['content'] = 'The book cannot be found in the book list. Pls check the book name and key in the book name again.'
            temp['messages'][0]['contentType'] = 'PlainText'
            temp['sessionState']['intent']['slots']['BookName']={}
            temp['sessionState']['intent']['slots']['StuEmail']={} 
            print(f'no match temp session state is {temp} \n') 
            return temp
      


    def update_session_state(self, user_id: str, temp: dict):
        """
        Updates the session state in Lex using the put_session method.
        """
        try:
            # Update the session state in Lex
            response = self.lex_client.put_session(
                botId=os.getenv('LEX_BOT_ID'),
                botAliasId=os.getenv('LEX_BOT_ALIAS_ID'),
                localeId='en_US',
                sessionId=user_id,
                sessionState=temp['sessionState'],
                messages=temp['messages']
            )
            print("Session state updated successfully.")
            # print(response) #response is hashed or sth
            print()

            return response
        except Exception as e:
            print(f"Error updating session state: {e}")
            raise e

    def handle_request(self, text: str, user_id: str) -> str:
        """
        Handles incoming user messages and interacts with Lex V2.
        """
        try:
            # Send user input to Lex V2
            response = self.lex_client.recognize_text(
                botId=os.getenv('LEX_BOT_ID'),
                botAliasId=os.getenv('LEX_BOT_ALIAS_ID'),
                localeId='en_US',
                sessionId=user_id,
                text=text
            )

            # Extract session state and slots
            session_state = response.get("sessionState", {})
            slots = session_state.get("intent", {}).get("slots", {})
            messages = response.get("messages", [])

            # Debugging: Print session state and slots
            print(f'Response is :{response}')
            print()

            print('get session state dialog action, slottoelicit')
            print(session_state['dialogAction'].get('slotToElicit'))
            print()

            # Validate Matric Number
            if session_state['dialogAction'].get('slotToElicit') and (session_state['dialogAction']['slotToElicit']=='BookName'):
                matric_num = slots['MatricNum']["value"]["interpretedValue"]
                print(f"Extracted MatricNum: {matric_num} \n")
                validation_response = self.matric_local_validation(matric_num, session_state, messages)
                print(f'validation response is {validation_response}')
                # futuer update: include checking of matricNumber

                self.update_session_state(user_id, validation_response)
                messages = validation_response['messages']

            # Validate Book
            if session_state['dialogAction'].get('slotToElicit') and (session_state['dialogAction']['slotToElicit']=='StuEmail'):
                book_name = slots['BookName']["value"]["interpretedValue"]
                print(f"Extracted BookName: {book_name} \n")
                validation_response = self.book_local_validation(book_name, session_state, messages)
                print(f'validation response is {validation_response}')
                # futuer update: include checking of matricNumber

                self.update_session_state(user_id, validation_response)
                messages = validation_response['messages']


            # Extract messages from Lex response
            if not messages:
                return "No response from bot."

            return "\n".join([msg["content"] for msg in messages])

        except Exception as e:
            print(f"Error communicating with AWS Lex: {e}")
            return "I encountered an error while processing your request."
