import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)
from transformers import pipeline
from typing import List

class Llama2JPModel:
    def __init__(self):
        self.MODEL_NAME = "elyza/ELYZA-japanese-Llama-2-7b-instruct"
        print(f"initializing model and tokenizer {self.MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(self.MODEL_NAME, torch_dtype="auto", device_map="auto")
        print("initialization complete. building pipeline...")
        # configuration
        self.max_output_tokens = 128
        self.pipeline = pipeline(
            task="text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=self.max_output_tokens,
            return_full_text=False,
        )
        print("model setup complete.")

    def generate(self, prompts:List[str]) -> List[dict]:
        output = self.pipeline(prompts, batch_size =len(prompts))
        return output