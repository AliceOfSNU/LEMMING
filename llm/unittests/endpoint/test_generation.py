import requests
import asyncio
import time
import aiohttp

def test_multiple_generation():
    loop = asyncio.get_event_loop()

    async def fetch(session, url):
        payload = {
            "words": ["慣れる", "呼ぶ", "起きる"]
        }
        result = None
        start_time = time.time()
        async with session.post(url, json=payload) as response:
            res = await response.json()
            end_time = time.time()
            print(f"query returned with time {end_time-start_time}, code {response.status}")
            result = {"time" : end_time-start_time, "status":response.status, "response": res}
        return result

    async def main():
        # launch queries
        ENDPOINT = "http://79.160.189.79:14515/generate_sentences"
        tasks = []
        async with aiohttp.ClientSession() as session:
            for i in range(10):
                print(f"spawned query {i}")
                tasks.append(asyncio.ensure_future(fetch(session, ENDPOINT)))
                await asyncio.sleep(5.0)
            # wait for queries to complete. hold on. this takes time
            tasks_results = await asyncio.gather(*tasks)
        
        # statistics
        total_time = 0.0
        succeeded_task_cnt = 0
        rid = 0
        for resdict in tasks_results:
            total_time += resdict["time"]
            if resdict["status"] == 200:
                succeeded_task_cnt += 1
            rid += 1
        avg_time = total_time / succeeded_task_cnt
        print("avg_time(s): ", avg_time)    
        print("success_rate: ", succeeded_task_cnt/rid)    

    # run 
    loop.run_until_complete(main())
    loop.close()

# main
test_multiple_generation()