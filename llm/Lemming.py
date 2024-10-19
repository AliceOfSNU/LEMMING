from prompt.prompters import Llama2JPPrompter, Llama3JPPrompter
from model.Llama2JPModel import Llama2JPModel, NetworkLLMWorker, ThreadedLLMWorker
from typing import List, Dict
import re
import queue
import asyncio
import random
import uuid
import time

MAX_QUEUE_SIZE = 5
class LemmingService:
    def __init__(self):
        self.prompter = Llama3JPPrompter()
        self.sync_queue: queue.Queue    = queue.Queue()
        self.job_queue: queue.Queue     = queue.Queue()
        self.result_queue: queue.Queue  = queue.Queue()
        self.awaited_jobs : Dict[str, List[asyncio.queue]] = {}
        #self.model = NetworkLLMWorker()
        self.model = ThreadedLLMWorker(self.job_queue, self.result_queue)
        self.loop: asyncio.Task = asyncio.create_task(self._poll_queue_loop())
        self.shutdown = False

    async def _poll_queue_loop(self):
        # pull tasks out of queue and dispatch to llm.
        while not self.shutdown:
            if self.sync_queue.qsize() > 0:
                # there is at least one item to process
                batch, qs = [], []
                while len(batch) < 4 and self.sync_queue.qsize() > 0:
                    (q, prompt) = self.sync_queue.get()
                    batch.append(prompt)
                    qs.append(q)
                uid = uuid.uuid1().hex
                print(f"queued batch <{uid}> with n={len(batch)}")
                self.job_queue.put((uid, batch))
                self.awaited_jobs[uid] = qs
            
            # poll result queues
            while self.result_queue.qsize() > 0:
                (uid, results) = self.result_queue.get()
                qs = self.awaited_jobs.pop(uid)
                print(f"completed batch <{uid}>")
                # iterate items of the batch and put result in corresponding queue
                for (q, res) in zip(qs, results):
                    await q.put(res)

            # wait for a little time before polling again.
            await asyncio.sleep(0.1)

    async def _create_generation_task(self, prompt: List[str]):
        if self.queue.qsize() > MAX_QUEUE_SIZE:
            return None
        q = asyncio.Queue()
        print(f"queue size {self.queue.qsize()}")
        self.queue.put((q, prompt))
        return q

    def postprocess(self, text: str) -> List[str]:
        sentences = re.split("\n[0-9][. ]*", text)
        sentences = [sent.strip() for sent in sentences[1:]]
        return sentences
    
    async def generate_sentences(self, word):
        prompt = self.prompter.prompt_generate_sentences(word)
        q = await self._create_generation_task(prompt)

        # server is too busy. client should try later
        if q is None:
            output = {"word": word, "sentences": [], "status": 1}
            print(f"canceled word {word}")
            return output
        
        print(f"put word {word} in queue")
        start = time.time()        
        output = await q.get()
        print(f"completed word {word} in {time.time()-start}seconds")

        # postproccessing
        output = self.postprocess(output)

        output = {"word": word, "sentences": output, "status": 0}
        return output


    async def generate_sentences_old(self, words: List[str]) -> List[dict]:
        # create batch prompt
        prompts = []
        for word in words:
            prompts.append(self.prompter.prompt_generate_sentences(word))
        
        # run through model
        model_outputs = []
        for prompt in prompts:
            print("start generation")
            output = await self.model.generate(prompt)
            # extract actual sentences from generated output
            print(output)
            model_outputs.append(output)

        results = []
        for output in model_outputs:
            sentences = re.split("\n[0-9][. ]*", output[0]["generated_text"])
            sentences = [sent.strip() for sent in sentences[1:]]
            # place the sentences into a result object, and append that object to list
            results.append({"count": len(sentences), "sentences": sentences})
        return results

    
    def generate_paragraph(self, subject: List[str]) -> List[dict]:
        raise NotImplementedError()
    
