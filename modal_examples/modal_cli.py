# # modal direct inference, see: modal_direct_inference_example.py

import modal
from src.secret import MODAL_APP_NAME, MODAL_BOT_DESCRIPTION, DEFAULT_ERROR_RESPONSE


def receive_data(msg: str, history: list[list] | None = None) -> list[str]:
    if len(msg) <= 1:
        return [msg, DEFAULT_ERROR_RESPONSE]
    try:
        f = modal.Function.lookup(MODAL_APP_NAME, "Model.generate")
        res = f.remote(
            MODAL_BOT_DESCRIPTION,
            [
                {
                    "prompt": msg,
                    "history": [] if not history else history
                }
            ]
        )
        return [msg, res[0]["response"]]
    except:
        return [msg, DEFAULT_ERROR_RESPONSE]
