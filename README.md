# modal_llm_xenforo_chatbot

## Chatbot for Xenforo using open source LLM model running on modal.com. <img alt="lol super" src="https://www.ignboards.com/styles/ign/ign/smilies/international-classic/lolsuper.gif">



## Requirements

- python 3.11
- ```xf_user``` User's logged in browser cookies added to ```src/secret.py``` file

## Usage

Any user can call the bot from any thread just by mentioning the nickname of the account that will be used as the bot. Example:
> **@Xenbot** What is 5 plus 5?

or reply to bot's response:
>> Xenbot said: 5 plus 5 equals 10!.
>> 
> add 3?

The bot saves interactions to continue the conversation if quoted (default 3).

<img alt="demo" src="https://i.imgur.com/zdBgMO3.png">

