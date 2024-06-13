import aiohttp
import asyncio
import logging
import json
import aiofiles
import pycountry
from itertools import islice
from functools import reduce
from asyncio import TimeoutError


logger =  logging.getLogger('checker')

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
    try:return reduce(lambda d, key: d[key], keys, data)
    except:return None

def soup_path(soup , selector , text):
    data =  soup.select_one(selector)
    if text:
        return data.get_text(strip=True) if data else None
    else:
        return data

def content_path(data ,  key ,  api , text  =  True ):
    return json_path(data,key) if api  ==  True else soup_path(data,key,text)

def country(co):
    try:return pycountry.countries.search_fuzzy(co)[0].alpha_3
    except :
        logger.warning(f'co country in {co}')
        return "NONE"

async def site_params(proxy , site_pa):
    return ( 
            "%s://%s:%s" % (content_path(proxy,site_pa["protocol"],site_pa["api"]) or "http",
            content_path(proxy,site_pa["ip"],site_pa["api"]),
            content_path(proxy,site_pa["port"],site_pa["api"]) ),
            content_path(proxy,site_pa["protocol"],site_pa["api"]) or "http",
            country(content_path(proxy,site_pa["country"],site_pa["api"]))
    )

async def check_proxy(proxy , site_pa):
    l_proxy , protocol , country = await site_params(proxy,site_pa)
    logger.debug(f"[proxy : {l_proxy}] [ protocol : {protocol}]  [country :  {country}]")
    url = 'http://httpbin.org/ip'  
    connector = aiohttp.TCPConnector(limit=None) 
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url,headers={},proxy=l_proxy,timeout=3) as response:
                if response.status == 200:
                    logger.debug(f'added : {l_proxy}')
                    await add_value_to_json(country=country,protocol=protocol,value=l_proxy)
                else:
                    logger.warning(f"Failed to connect through {l_proxy}. Status code: {response.status}")
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
    proxies =content_path(data,site['proxies'],site['api'],text=False)
    await print_when_done((check_proxy(proxy,site)  for proxy in proxies))

