"""
A script to practice making concurrent requests using aiohttp.
The script stops making requests when a condition is met. This is done
using asyncio.Event
"""


import pandas as pd
import json
import aiohttp
import asyncio

from aiohttp import ClientSession

CRIME_DATA_URL_2017 = "https://data.cityofchicago.org/resource/d62x-nvdr.json?$limit=1000&$offset={}"

async def get_request_json(url: str, client: ClientSession):
    resp = await client.request(method="GET", url=url)
    resp.raise_for_status()
    text = await resp.text()
    json_data = json.loads(text)
    print("done with {}".format(url))
    return json_data
 

async def parse_json_into_df(url: str, client: ClientSession):
    json_resp = await get_request_json(url=url, client=client)
    df = pd.DataFrame.from_dict(json_resp)
    return df

async def main():
    flag = asyncio.Event()
    offset = 0
    total_run = 0

    async with aiohttp.ClientSession() as session:
        while 1:
            tasks = []
            for _ in range(0, 10):
                curr_url = CRIME_DATA_URL_2017.format(offset)
                tasks.append(parse_json_into_df(url=curr_url, client=session))
                offset += 1000
            await asyncio.gather(*tasks)

            total_run += 1
            # stop at second batch of api calls
            if total_run == 2:
                flag.set()
            
            if flag.is_set():
                break

loop = asyncio.new_event_loop()
ans = loop.run_until_complete(main())