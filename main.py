import aiohttp
import asyncio
import json
from checker import  checker

async def fetch_json(session, site,headers):
    async with session.get(site['url'],headers =  headers) as response:
        return  {"site":site,"res": await response.json()}
    
async def fetch_soup(session, url,headers):
    async with session.get(url,headers =  headers) as response:
        return await response.text()


def get_sites():
    with open("sites.json","r") as f: return json.loads(f.read())

async def fetch_all():

    sites  = get_sites()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
                                            'Referer': "refer",}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for site in sites:
            tasks.append(fetch_json(session, site  ,headers=headers)
                        if site['api'] == True  
                        else fetch_soup(session,site['url'],headers=headers) )
            
        responses = await asyncio.gather(*tasks)
        return responses




async  def main():

    resulst =  await fetch_all()

    await asyncio.gather(*[checker(res['site'],data=res['res']) for res in resulst])

asyncio.run(main())
