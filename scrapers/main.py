import asyncio
from datetime import datetime
import json
import os

import boto3
from dotenv import load_dotenv

from curator import curator
from sfu import sfuScraper
from ubc import ubcScraper

schoolToScraper = [
    {
        "schoolName": "simon_fraser_university",
        "scraper": sfuScraper.extractData,
    },
    {
        "schoolName": "university_of_british_columbia",
        "scraper": ubcScraper.getAllData,
    }
]

async def runTasks():
    for task in schoolToScraper:
        schoolName = task['schoolName']
        f = task['scraper']
        print(f'Start running {schoolName}')

        s3 = boto3.client('s3')
        load_dotenv()
        try:
            # data: dict
            print("Scraping starts\n")
            data = await f()
            serializedData = json.dumps(data)
            print("Done scraping\n")

            key = schoolName + "/" + str(datetime.now().year) + "/" + str(datetime.now().month) + "/" + str(datetime.now().day)
            print(f"Storing data {key}")
            s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=key, Body=serializedData)
            
            print('cleansed stored')
            await curator.update(key, schoolName)
            print(f'${schoolName} done')
        except:
            return

if __name__ == '__main__':
    asyncio.run(runTasks())
        
