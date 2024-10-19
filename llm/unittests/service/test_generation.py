# this file contains tests that checks the generation pipeline,
# both for sentences and paragrpahs, works properly.

from typing import List, Dict
import os
import csv
import asyncio
import Lemming
import time

TEST_OUTPUT_DIR = "unittests/outputs"
def write_to_csv(title: str, data: List[List[str]]):
    with open(os.path.join(TEST_OUTPUT_DIR, title), "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)


async def test_generate_sentences():
    words = ["動く","移す","話す","抱く"]
    await asyncio.sleep(1.0)
    data = [["word", "sentence"]]

    lemming = Lemming.LemmingService()

    # create some tasks
    tasks = []
    startup = time.time()
    for i in range(50):
        print(f"req@ {time.time()-startup}, task#{i}")
        tasks.append(asyncio.create_task(lemming.generate_sentences("動く")))
        await asyncio.sleep(0.3)

    # wait for all tasks to complete
    tasks_results = await asyncio.gather(*tasks)

    # see results
    for results in tasks_results:
        print(results)

    lemming.shutdown = True
    await lemming.loop

    sum = 0.0
    for t in lemming.durations:
        sum += t
    print(f"mean latency: {sum/len(lemming.durations)}")



#if __name__ == "__main__":
asyncio.run(test_generate_sentences())

