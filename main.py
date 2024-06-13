import aiohttp
import asyncio
import logging
import json

from bs4 import BeautifulSoup 

from checker import  checker


logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
    handlers=[
        logging.FileHandler("logs.log"), 
        logging.StreamHandler() 
    ]
)


logger =  logging.getLogger('main')



async def fetch_json(session, site):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
                'Referer': site["site"]
                }
    
    async with session.get(site['url'],headers =  headers) as response:
        logger.info(f"{site['url']} collcted proxies")
        return  {"site":site,"res": await response.json()}
    
async def fetch_soup(session, site):


    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
                'Referer': site["site"]
                }
    
    async with session.get(site["url"],headers =  headers) as response:
        logger.info(f"{site['url']} collcted proxies")
        return {"site":site,"res": BeautifulSoup( await response.text() , "html.parser")}
        


def get_sites():
    with open("sites.json","r") as f: return json.loads(f.read())

async def fetch_all():

    sites  = get_sites()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for site in sites:
            tasks.append(fetch_json(session, site)
                        if site['api'] == True  
                        else fetch_soup(session,site) )
            
        responses = await asyncio.gather(*tasks)
        return responses




async  def main():

    logger.info('< executing PRPXYHARVEST >')

    resulst =  await fetch_all()

    await asyncio.gather(*[checker(res['site'],data=res['res']) for res in resulst])

asyncio.run(main())
