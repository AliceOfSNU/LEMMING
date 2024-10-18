# this file contains tests that checks the generation pipeline,
# both for sentences and paragrpahs, works properly.

from typing import List, Dict
import os
import csv
import asyncio
import Lemming
import matplotlib
import matplotlib.pyplot as plt
import time
import threading
import queue

TEST_OUTPUT_DIR = "unittests/outputs"
def write_to_csv(title: str, data: List[List[str]]):
    with open(os.path.join(TEST_OUTPUT_DIR, title), "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)

#lemming = Lemming.LemmingService()


def test_threaded_requests():
    TASK_QUEUE_MAX_SIZE = 4
    job_queue = queue()
    job_res_queue = queue()    
    class HFThread():        
        def run(self):
            while True:
                (data, qid) = job_queue.get()
                time.sleep(1)
                job_res_queue.put((data + " done", qid))
                print(f"finished processing #{qid}, remaining queue {job_queue.qsize()}")
    
    qmap = {}

    async def query(id:str):
        start_time = time.time()
        print(f"task {id}")
        if job_queue.qsize() > TASK_QUEUE_MAX_SIZE:
            print(f"canceling task#{id}")
            result = -1
        else:
            response_q = asyncio.Queue()
            # place task in job queue and subscribe for notification
            print(f"putting in queue task#{id}")
            job_queue.put((f"minitask {id}", id))
            qmap[id] = response_q

            # awake when job is done
            _ = await response_q.get() 
            result = time.time() - start_time
        return result

    async def poll_results_loop():
        while(True):
            (result, qid) = job_res_queue.get() # fetch result
            await qmap[qid].put(result) # notify corresponding coroutine
            await asyncio.sleep(0.1)
            
    async def main():
        # launch queries
        tasks = []
        server = asyncio.create_task(poll_results_loop())

        for i in range(16):
            tasks.append(asyncio.create_task(query(str(i))))
            await asyncio.sleep(1.0)
        # wait for queries to complete. hold on. this takes time
        tasks_results = await asyncio.gather(*tasks)
        server.cancel()

        print(tasks_results)

    t1 = HFThread()
    t1.run()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

def test_multiple_requests():
    task_q = asyncio.Queue()
    TASK_QUEUE_MAX_SIZE = 4

    async def server_loop():
        words = ["動く","移す","話す","抱く"]
        while(True):
            (task, res_q) = await task_q.get()
            outputs = lemming.generate_sentences(words)
            print(f"server done generateing {task}, remaining in q: {task_q.qsize()}")
            await res_q.put(outputs)

    async def query(id:str):
        print(f"task {id}")
        start_time = time.time()
        if task_q.qsize() > TASK_QUEUE_MAX_SIZE:
            result = {"time": -1, "generation": []}
        else:
            response_q = asyncio.Queue()
            print(f"putting in queue task#{id}")
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
test_threaded_requests()
