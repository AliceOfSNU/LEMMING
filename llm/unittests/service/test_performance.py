# this file contains tests that checks the generation pipeline,
# both for sentences and paragrpahs, works properly.

from typing import List, Dict
import os
import csv
import asyncio
#import Lemming
import matplotlib
import matplotlib.pyplot as plt
import time
import queue
import random
import threading 
TEST_OUTPUT_DIR = "unittests/outputs"
def write_to_csv(title: str, data: List[List[str]]):
    with open(os.path.join(TEST_OUTPUT_DIR, title), "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)

keep_going = True
#lemming = Lemming.LemmingService()
def test_threaded_requests():
    TASK_QUEUE_MAX_SIZE = 4
    job_queue = queue.Queue()
    job_res_queue = queue.Queue()    
    
    class HFThread(threading.Thread):        
        def count_to(self, n:int) -> float:
            sum = 0.0
            for i in range(n):
                sum += n
            return sum
        
        def run(self):
            global keep_going
            while keep_going:
                if job_queue.qsize() > 0:
                    (data, qid) = job_queue.get()
                    # simulates a cpu-bound task
                    # this does not block the main thread.
                    x = self.count_to(100000000)
                    job_res_queue.put((data + " done, result = " + str(x), qid))
                    print(f"finished processing #{qid}, remaining queue {job_queue.qsize()}")
                time.sleep(random.random()*0.1)

    qmap = {}
    server_start_time = time.time()

    async def query(id:str):
        start_time = time.time()
        if job_queue.qsize() >= TASK_QUEUE_MAX_SIZE:
            print(f"req@{start_time - server_start_time}, canceling task#{id}")
            result = -1
        else:
            response_q = asyncio.Queue()
            print(f"req@{start_time - server_start_time}, putting in queue task#{id}, qsize: {job_queue.qsize()}")
            # place task in job queue and subscribe for notification
            job_queue.put((f"minitask {id}", id))
            qmap[id] = response_q
            # awake when job is done
            _ = await response_q.get() 
            result = time.time() - start_time
        return result

    async def poll_results_loop():
        while(True):
            while job_res_queue.qsize() > 0:
                (result, qid) = job_res_queue.get() # fetch result
                await qmap[qid].put(result) # notify corresponding coroutine
            # polling result frequency..
            await asyncio.sleep(0.1)

    async def main():
        # launch queries
        tasks = []
        print("starting main")
        server = asyncio.create_task(poll_results_loop())
        for i in range(30):
            # requests queued at rate
            tasks.append(asyncio.create_task(query(str(i))))
            await asyncio.sleep(0.5)
        # wait for queries to complete. hold on. this takes time
        tasks_results = await asyncio.gather(*tasks)
        server.cancel()
        print(tasks_results)

    t1 = HFThread()
    t1.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    global keep_going
    keep_going = False
    t1.join()


def test_multiple_requests():
    task_q = asyncio.Queue()
    TASK_QUEUE_MAX_SIZE = 4
    server_start_time = time.time()

    # sync function
    def count_to(self, n:int) -> float:
        sum = 0.0
        for i in range(n):
            sum += n
        return sum
    
    async def server_loop():
        words = ["動く","移す","話す","抱く"]
        while(True):
            (task, res_q) = await task_q.get()
            #outputs = lemming.generate_sentences(words)
            n = 100000000
            sum = 0.0
            for i in range(n):
                sum += n
            outputs = sum
            # asyncio.sleep(1.0)
            print(f"finished generateing {task}, remaining in q: {task_q.qsize()}")
            await res_q.put(outputs)

    async def query(id:str):
        start_time = time.time()
        if task_q.qsize() > TASK_QUEUE_MAX_SIZE:
            print(f"req@{start_time - server_start_time}, canceling task {id}")
            result = {"time": -1, "generation": []}
        else:
            response_q = asyncio.Queue()
            print(f"req@{start_time - server_start_time}, putting in queue task#{id}")
            await task_q.put((f"minitask {id}", response_q))
            result = await response_q.get()
            end_time = time.time()
            result = {"time": end_time - start_time, "generation": []}
        return result

    async def main():
        # create server loop
        server = asyncio.create_task(server_loop())
        print("sever loop started")
        # launch queries
        tasks = []
        for i in range(16):
            tasks.append(asyncio.create_task(query(str(i))))
            await asyncio.sleep(1.0)
        # wait for queries to complete. hold on. this takes time
        tasks_results = await asyncio.gather(*tasks)
        server.cancel()
        
        # statistics
        total_time = 0.0
        succeeded_task_cnt = 0
        generated_sentences = []
        for resdict in tasks_results:
            if resdict["time"] != -1:
                total_time += resdict["time"]
                succeeded_task_cnt += 1
            for it in resdict["generation"]:
                generated_sentences.extend(it["sentences"])
        avg_time = total_time / succeeded_task_cnt
        print("avg_time(s): ", avg_time)    
        print("success_rate: ", succeeded_task_cnt/len(tasks_results))    
        write_to_csv("test_generate_sentences.csv", generated_sentences)

    # run 
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

#if __name__ == "__main__":
test_multiple_requests()
#test_threaded_requests()
