# TembusuLib
Conversation Chatbot for Tembusu Library

## Key modules
1. Telegram bot module

This module provides the access to telegram and it will make telegram connection to the conversation module.

2. Conversation module

This module provides access to various chatbot service. It started with AWS Lex. Next could be Google and maybe a LLM. 

This module will handle the conversation and validate the inputs with backend.

3. (Upcoming) Backend module 

Backend module will connect to DB for information validation, creation, update etc. 

## Keys and Secrets

The keys and secrets are currently handled and passed over offline, not coded here.


# Change Log
|Date|Description|
|---|---|
|2025 Mar 15| Decoupled the conversation handling from telegram module|
