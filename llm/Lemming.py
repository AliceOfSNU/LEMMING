from prompt.prompters import Llama2JPPrompter, Llama3JPPrompter
from model.Llama2JPModel import Llama2JPModel, NetworkLLMWorker, ThreadedLLMWorker
from typing import List, Dict
import re
import queue
import asyncio
import random
import uuid
import time

MAX_QUEUE_SIZE = 100
class LemmingService:
    def __init__(self):
        self.prompter = Llama3JPPrompter()
        self.sync_queue: queue.Queue    = queue.Queue()
        self.job_queue: queue.Queue     = queue.Queue()
        self.result_queue: queue.Queue  = queue.Queue()
        self.awaited_jobs : Dict[str, List[asyncio.queue]] = {}
        #self.model = NetworkLLMWorker()
        self.model = ThreadedLLMWorker(self.job_queue, self.result_queue)
        self.model.start()
        self.loop: asyncio.Task = asyncio.create_task(self._poll_queue_loop())
        self._shutdown = False
        self.last_tick = time.time()

        # debug
        self.n = 0
        self.durations = []
        self.batch_sizes = []
        self.q_sizes = []

    async def shutdown(self):
        self._shutdown = True
        await self.loop

    async def _poll_queue_loop(self):
        # pull tasks out of queue and dispatch to llm.
        MAX_BATCH_SIZE = 32
        MAX_WAIT_TIME = 0.4
        while not self._shutdown:
            if self.sync_queue.qsize() > MAX_BATCH_SIZE or (time.time() - self.last_tick) > MAX_WAIT_TIME:
                # there is at least one item to process
                batch, qs = [], []
                while len(batch) < MAX_BATCH_SIZE and self.sync_queue.qsize() > 0:
                    (q, prompt) = self.sync_queue.get()
                    batch.append(prompt)
                    qs.append(q)
                if len(batch) > 0:
                    uid = uuid.uuid1().hex
                    print(f"queued batch <{uid}> with n={len(batch)}")
                    self.batch_sizes.append(len(batch))
                    self.job_queue.put((uid, batch))
                    self.awaited_jobs[uid] = qs
                self.last_tick = time.time()
            
            # poll result queues
            while self.result_queue.qsize() > 0:
                (uid, results) = self.result_queue.get()
                qs = self.awaited_jobs.pop(uid)
                # print(f"completed batch <{uid}>")
                # iterate items of the batch and put result in corresponding queue
                for (q, res) in zip(qs, results):
                    await q.put(res)

            # wait for a little time before polling again.
            await asyncio.sleep(0.1)

        self.model.shutdown = True
        self.model.join()

    async def _create_generation_task(self, prompt: List[str]):
        if self.sync_queue.qsize() > MAX_QUEUE_SIZE:
            return None
        q = asyncio.Queue()
        print(f"queue size {self.sync_queue.qsize()}")
        self.q_sizes.append(self.sync_queue.qsize())
        self.sync_queue.put((q, prompt))
        return q

    def postprocess(self, text: str) -> List[str]:
        text = "discard" + text # add header so it can be discarded
        sentences = re.split("\n[0-9][. ]*", text)
        sentences = [sent.strip() for sent in sentences[1:]]
        return sentences
    
    async def generate_sentences(self, word):
        prompt = self.prompter.prompt_generate_sentences(word)
        if self.n == 0:
            print(prompt)
            self.n += 1
        q = await self._create_generation_task(prompt)

        # server is too busy. client should try later
        if q is None:
            output = {"word": word, "sentences": [], "status": 1}
            # print(f"canceled word {word}")
            return output
        
        start = time.time()        
        output = await q.get()
        print(f"completed word {word} in {time.time()-start}seconds")
        self.durations.append(time.time()-start)

        # postproccessing
        output = self.postprocess(output)

        output = {"word": word, "sentences": output, "status": 0}
        return output

    
    def generate_paragraph(self, subject: List[str]) -> List[dict]:
        raise NotImplementedError()
    
