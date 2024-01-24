import requests

from src.secret import (
    USER_AGENT,
    API_SECRET_TOKEN,
    MODAL_URL,
    MODAL_BOT_DESCRIPTION,
    DEFAULT_ERROR_RESPONSE,
    LOGGING_ENABLED
)

headers = {
    "User-Agent": USER_AGENT,
    "Content-Type": "application/json"
}


def receive_data(msg: str, history: list[list] | None = None) -> list[str]:
    if len(msg) <= 1:
        return [msg, DEFAULT_ERROR_RESPONSE]

    payload = {
        "key": API_SECRET_TOKEN,
        "bot_description": MODAL_BOT_DESCRIPTION,
        "prompts": [
            {
                "prompt": msg,
                "history": [] if not history else history
            }
        ]
    }
    try:
        response = requests.post(MODAL_URL, headers=headers, json=payload)
        response.raise_for_status()
        response = response.json()
        if LOGGING_ENABLED:
            print(response)
        return [msg, response[0]["response"]]
    except requests.RequestException:
        return [msg, DEFAULT_ERROR_RESPONSE]
