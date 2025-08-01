# TembusuLib
Conversation Chatbot for Tembusu Library

## Key modules

```
main.py
telegram_bot.py
Dockerfile

credentials/ # .gitignored
└── google service account .json

conversation_module/
├── __init__.py
├── lex_handler.py
├── dialogflow_handler.py
└── custom_handler/
    ├── __init__.py
    ├── core.py
    ├── component_borrow.py
    ├── component_common.py
    ├── component_extendloan.py
    ├── component_faq.py # contributed by Ruofan
    ├── component_loanrecord.py
    ├── component_return.py
    └── component_search.py # contributed by Ruofan

notification/
└── due_date_notifier.py # contributed by Ruofan

utils/
├── auth_helpers.py
├── date_parser.py
├── db_add_borrow.py
├── db_book_validator.py
├── db_extend_loan.py
├── db_loan_history.py
├── db_location_validator.py
├── db_return_book.py
├── db_search_book.py
├── db_student_validator.py
├── db_telegramid_validator.py
├── photo_cleaning.py
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

- notification/
    - This is the module that provide notification to user (student) and remind them to return books.

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
export PHOTO_CLEANING_INTERVAL='xxx'
export MAX_FILE_AGE_SECONDS='xxx'
export MAX_BORROW_LIMIT='xxx'
```

# Docker-related setup
In order for the chatbot to work on docker, we need to make sure all the db base url uses db:8000 instead of localhost:8000

We also need to include the Dockerfile under the folder where the project runs.

# Change Log
|Date|Description|
|---|---|
|2025 Mar 15| Decoupled the conversation handling from telegram module|
|2025 Mar 16| <li> Added validation of MatricNumber (to follow format "letter-7digits-letter") and</li><li> book name (from a book list that's set in self.bookList)</li>|
|2025 May 16| Updated the utility backend service and how to run code.|
|2025 May 20| Updated the docker related content.|
|2025 Aug 01| Updated conversation flows according to user requirement. Included some chores like cleaning photos submitted by users. Included the code contribution by Ruofan (the notification funciton, conversation for faq and search).|

