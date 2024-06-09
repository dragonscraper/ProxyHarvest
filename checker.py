import aiohttp
import asyncio
import json
import aiofiles
import pycountry
from itertools import islice
from functools import reduce
from asyncio import TimeoutError


data_p =  "proxies.json"

DATA  = {}

async def add_value_to_json(file_path=data_p, country = None ,
                             protocol = None , value =  None):
    if DATA.get(country) is None:
        DATA[country] = {protocol:[value]}
    
    elif DATA[country].get(protocol) is None:
        DATA[country][protocol] = [value]
    else:
        DATA[country][protocol].append(value)

    async with aiofiles.open(file_path, mode='w') as f:
        await f.write(json.dumps(DATA,indent=4))

def json_path(data , keys :  list):
    return reduce(lambda d, key: d[key], keys, data)

def country(co):
    try:return pycountry.countries.search_fuzzy(co)[0].alpha_3
    except :return "NONE"

async def site_params(proxy , site_pa):
    return  (json_path(proxy,site_pa["l_proxy"]) ,
             json_path(proxy,site_pa["protocol"]),
             country(json_path(proxy,site_pa["country"]))
             ) if site_pa["api"] ==  True else (
                 
             )


async def check_proxy(proxy , site_pa):
    l_proxy , protocol , country = await site_params(proxy,site_pa)
    url = 'http://httpbin.org/ip'  
    connector = aiohttp.TCPConnector(limit=None) 
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url,headers={},proxy=l_proxy,timeout=3) as response:
                if response.status == 200:
                    await add_value_to_json(country=country,protocol=protocol,value=l_proxy)
                else:
                    print(f"Failed to connect through proxy. Status code: {response.status}")
        except TimeoutError as e:
            pass

        except Exception as e:
            pass




def limited_as_completed(coros, limit):
    futures = [
        asyncio.ensure_future(c)
        for c in islice(coros, 0, limit)
    ]
    async def first_to_finish():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        newf = next(coros)
                        futures.append(
                            asyncio.ensure_future(newf))
                    except StopIteration as e:
                        pass
                    return f.result()
    while len(futures) > 0:
        yield first_to_finish()

async def print_when_done(tasks):
    for res in limited_as_completed(tasks, 40 ):
        await res


async def  checker(site , data):
    proxies = json_path(data,site['proxies']) if site['api'] == True else None
    await print_when_done((check_proxy(proxy,site)  for proxy in proxies))

