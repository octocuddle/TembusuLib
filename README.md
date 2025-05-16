# TembusuLib
Conversation Chatbot for Tembusu Library

## Key modules
```
main.py
telegram_bot.py
conversation_module/
├── __init__.py
├── lex_handler.py
├── dialogflow_handler.py
└── custom_handler/
    ├── __init__.py
    ├── core.py
    ├── component_borrow.py
    ├── component_common.py
    ├── component_loanrecord.py
    └── component_photo.py
utils/
├── db_add_borrow.py
├── db_book_validator.py
├── db_loan_history.py
├── db_student_validator.py
└── qr_decoder.py
```



**1. Telegram bot module**

This module provides the access to telegram and it will make telegram connection to the conversation module.

**2. Conversation module**

This module provides access to various chatbot service. It started with AWS Lex. Next could be Google and maybe a LLM. 

This module will handle the conversation and validate the inputs with backend.

**3. Backend module**

Backend module will connect to DB for information validation, creation, update etc. 

- utils/
    - This is the modules handles some db CRUD and some additional activities like QR code scanning.

- Maybe more backend services will be provided

## Dependencies and how to run the code

### Install Zbar on local environment

This project requires the ZBar library for reading QR code and Zbar needs to be installed on your system:
- On macOS: brew install zbar
- On Ubuntu/Debian: sudo apt install libzbar0

As there is a need to install zbar on the local laptop so that the chatbot can read qr code, the zbar package is installed somewhere in the laptop.

If installation caused error due to multiple python version installed in the local environment, the programme need to appoint to where zbar is installed and run with the following code:
- `DYLD_LIBRARY_PATH="/opt/homebrew/lib" /usr/local/bin/python3 main.py`

Otherwise, the normal `python3 main.py` is sufficient.

### Activate the virtual environment of Database
The database should be running:
- Run PostgreSQL at any terminal `psql -U testuser MyLibrary2` (assuming the databse already have some initiated data inside)
- Navigate to the databse repo local code, attach an integrated terminal
- Activate the virutal environment `source venv/bin/activate`
- Run the fastAPI app: `uvicorn app.main:app --reload`


## Keys and Secrets

The keys and secrets are currently handled and passed over offline, not coded here.

Latest secrets include:
```
export AWS_ACCESS_KEY_ID='xx'
export AWS_SECRET_ACCESS_KEY='xxx'
export AWS_DEFAULT_REGION='xxx'
export TELEGRAM_TOKEN='xxx'
export LEX_BOT_ID='xxx'
export LEX_BOT_ALIAS_ID='xxx'
export GOOGLE_APPLICATION_CREDENTIALS="/Users/.../.../xxx.json"
export DIALOGFLOW_PROJECT_ID="xxx"
```

# Change Log
|Date|Description|
|---|---|
|2025 Mar 15| Decoupled the conversation handling from telegram module|
|2025 Mar 16| <li> Added validation of MatricNumber (to follow format "letter-7digits-letter") and</li><li> book name (from a book list that's set in self.bookList)</li>|
|2025 May 16| Updated the utility backend service and how to run code.|

