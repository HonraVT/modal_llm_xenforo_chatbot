import requests

from src.secret import USER_AGENT, API_SECRET_TOKEN, MODAL_URL, DEFAULT_ERROR_RESPONSE, LOGGING_ENABLED

headers = {
    "User-Agent": USER_AGENT,
    "Content-Type": "application/json"
}


def receive_data(msg: str, history: list[list] | None = None) -> list[str]:
    if len(msg) <= 1:
        return [msg, DEFAULT_ERROR_RESPONSE]

    payload = {
        "key": API_SECRET_TOKEN,
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


# import modal
# from src.secret import MODAL_APP_NAME, DEFAULT_ERROR_RESPONSE
#
#
# def receive_data(msg: str, history: list[list] | None = None) -> list[str]:
#     if len(msg) <= 1:
#         return [msg, DEFAULT_ERROR_RESPONSE]
#     try:
#         f = modal.Function.lookup(MODAL_APP_NAME, "Model.generate")
#         res = f.remote([
#             {
#                 "prompt": msg,
#                 "history": [] if not history else history
#             }
#         ])
#         if LOGGING_ENABLED:
#             print(res)
#         return [msg, res[0]["response"]]
#     except:
#         return [msg, DEFAULT_ERROR_RESPONSE]
