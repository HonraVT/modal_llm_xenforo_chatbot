# Register on modal.com with your GitHub account. Follow these steps:
# 1. Create a new virtual environment with Python 3.11.
# 2. Install the Modal library: `pip install modal`.
# 3. Ignore IDE errors; Modal will execute the code in the cloud.
# 4. Configure Modal and obtain the token authorization file: `python -m modal setup`.
# 5. Generate a Hugging Face token at https://huggingface.co/settings/tokens to avoid download issues.
# 6. On the Modal dashboard's "Secrets" tab, create a new secret named "my-huggingface-secret" with key: `HUGGINGFACE_TOKEN` and value: "your Hugging Face token."
# 7. Create another secret named "bot-secrets" with key: `API_TOKEN` and value: "your random 16-character confidential password."
# 8. Run the file using: `modal deploy modal_api_example.py`.
# 9. Wait for Modal to install and get your URL endpoint printed on the console.
# 10. Set this URL as "MODAL_URL" in the `src.secret.py` file.


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


def format_prompts(prompts: list[dict]) -> list[str]:
    result = []
    for item in prompts:
        output = ("### System:\nYou are Vtlore a helpful AI assistant. You always answer briefly in a few words, "
                  "at most two or three lines of text and never create long lists. You always respond in Brazilian "
                  "Portuguese\n\n")
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
    def generate(self, user_questions: list[dict]) -> list[dict]:
        from vllm import SamplingParams

        prompts = format_prompts(user_questions)

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
                {
                    "status": 0,
                    "prompt": user_questions[index]["prompt"],
                    "response": output.outputs[0].text,
                    "tokens": num_tokens
                }
            )
        return res


class Item(BaseModel):
    key: str
    prompts: list


@stub.function(secret=modal.Secret.from_name("bot-secrets"))
@web_endpoint(method="POST")
def f(item: Item):
    if item.key != os.environ["API_TOKEN"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )
    model = Model()
    res = model.generate.remote(item.prompts)
    return res
