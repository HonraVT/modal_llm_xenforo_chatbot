# first you need register on modal.com with your GitHub account.
# steps:
# Create a new virtual environment with python 3.11.
# install modal lib (add modal to requirements.txt) with: pip install modal
# Don't worry about errors in your IDE from imports inside functions, Modal will run the code in the cloud.
# Configure modal (get token authorization file): python -m modal setup
# create a huggingface token at https://huggingface.co/settings/tokens to not be blocked at download weights.
# now set a new "secrets" on modal dashboard -> secrets tab
# select "custom" add key: HUGGINGFACE_TOKEN value: "your huggingface token" and add a name: my-huggingface-secret
# After run this file with: modal deploy modal_direct_inference_example.py
# Wait modal internally installs and set "MODAL_APP_NAME" in src.secret.py file with your app name (line 67).
# comment "modal_cli api client" from secrets file.
# and change code in src.modal_cli.py with code in modal_cli.py from this folder.


import os

import modal
from fastapi import HTTPException, status
from modal import Image, Secret, Stub, method, web_endpoint
from pydantic import BaseModel

MODEL_DIR = "/model"
BASE_MODEL = "w4r10ck/SOLAR-10.7B-Instruct-v1.0-uncensored"


def download_model_to_folder():
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        BASE_MODEL,
        local_dir=MODEL_DIR,
        token=os.environ["HUGGINGFACE_TOKEN"],
    )
    move_cache()


def format_prompts(bot_description: str, prompts: list[dict]) -> list[str]:
    result = []
    for item in prompts:
        output = (
            f"### System:\nYou are {bot_description}. You always answer briefly in a few words, "
            "at most two or three lines of text and never create long lists. You always respond in Brazilian "
            "Portuguese\n\n"
        )
        for q, a in item["history"]:
            output += f"### User:\n{q}\n\n### Assistant:\n{a}\n\n"
        output += f"### User:\n{item['prompt']}\n\n### Assistant:"
        result.append(output)
    return result


image = (
    Image.from_registry(
        "nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10"
    )
    .pip_install("vllm==0.2.5", "huggingface_hub==0.19.4", "hf-transfer==0.1.4")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_folder,
        secret=modal.Secret.from_name("my-huggingface-secret"),
        timeout=60 * 20,
    )
)

stub = Stub("example-vllm-inference", image=image)


@stub.cls(gpu="A100", secret=Secret.from_name("my-huggingface-secret"))
class Model:
    def __enter__(self):
        from vllm import LLM

        self.llm = LLM(MODEL_DIR)

    @method()
    def generate(self, bot_desc: str, user_questions: list[dict]) -> list[dict]:
        from vllm import SamplingParams

        prompts = format_prompts(bot_desc, user_questions)

        sampling_params = SamplingParams(
            temperature=0.75,
            top_p=1,
            max_tokens=800,
            presence_penalty=1.15,
        )
        result = self.llm.generate(prompts, sampling_params)
        num_tokens = 0
        res = []
        for index, output in enumerate(result):
            num_tokens += len(output.outputs[0].token_ids)
            res.append(
                {"status": 0,
                 "prompt": user_questions[index]["prompt"],
                 "response": output.outputs[0].text,
                 "tokens": num_tokens
                 }
            )
        return res
