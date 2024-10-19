from typing import List
import threading
import subprocess
import aiohttp
import time
import os
import atexit
import queue
import asyncio

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)
from vllm import LLM, SamplingParams

class LLMModel():
    def __init__(self):
        self.tokenizer = None
        self.model = None
    
    def generate(self):
        raise NotImplementedError

class Llama2JPModel(LLMModel):
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
    
class Llama3JPModel():
    def __init__(self):
        self.llm = LLM(model="elyza/Llama-3-ELYZA-JP-8B-AWQ", quantization="awq")
        self.tokenizer = self.llm.get_tokenizer()
        self.sampling_params = SamplingParams(temperature=0.6, top_p=0.9, max_tokens=600)
    
    def generate(self, batch_prompts: List[List[str]]):
        prompts = [
            self.tokenizer.apply_chat_template(prompt, tokenize = False, add_generation_prompt=True)
            for prompt in batch_prompts
        ]
        outputs = self.llm.generate(prompts, self.sampling_params)
        outputs = [
            res.outputs[0].text for res in outputs
        ]
        return outputs
    
    
class ThreadedLLMWorker(threading.Thread):
    def __init__(self, job_queue, result_queue):
        super().__init__()
        self.job_queue = job_queue
        self.result_queue = result_queue
        self.model = Llama3JPModel()
        self.shutdown = False

    # this function is synchronous,
    # will not block the main thread
    def run(self):
        print("llm thread has started")
        while not self.shutdown:
            if self.job_queue.qsize() > 0:
                (uid, batch) = self.job_queue.get()
                start_time = time.time()
                print(f"[gen] started for <{uid}>")
                outputs = self.model.generate(batch)
                print(f"[gen] in {time.time()-start_time} seconds")
                self.result_queue.put((uid, outputs))
            time.sleep(0.1)


class NetworkLLMWorker():
    def __init__(self, port:int = 8000, host:str = "localhost"):
        self.model_str = "elyza/Llama-3-ELYZA-JP-8B-AWQ"
        self.completion_ep = f"http://{host}:{str(port)}/v1/chat/completions"
        callargs = [
            "python",
            "-m", "vllm.entrypoints.openai.api_server",
            "--model", self.model_str,
            "--port", str(port),
            "--host", host,
            "--quantization", "awq",
        ]
        print("initializing server")
        #self.srv_process = subprocess.Popen(callargs, shell=True)
        #print("started server. pid: ", self.srv_process.pid)
        #atexit.register(self.srv_process.terminate)

    async def generate(self, prompts:List[str], **generation_args):
        payload = {
            "model": self.model_str,
            "messages": prompts,
            **generation_args,
        }
        start_time = time.time()
        await asyncio.sleep(1.0)
        result = "A\n1.one\n2.two\n3.three"
        #async with aiohttp.ClientSession() as session:
        #    async with session.post(self.completion_ep, json=payload) as response:
        #        res = await response.json()
        #        latency = time.time()-start_time
        #        result = {"time" : latency, "response": res}
        return result
