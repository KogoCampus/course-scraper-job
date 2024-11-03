import asyncio
from datetime import datetime
import json
import os

import boto3
from dotenv import load_dotenv

from converter import cleanseSFU
import curator
import sfuScraper
import ubcScraper

schoolToScraper = [
    {
        "schoolName": "simon_fraser_university",
        "scraper": sfuScraper.extractData,
        "cleanse": cleanseSFU,
    },
    # {
    #     "schoolName": "university_of_british_columbia",
    #     "scraper": ubcScraper.getAllData,
    # }
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
            data = await f()
            serializedData = json.dumps(data)

            # needs cleansing
            if task.get('cleanse'):
                uncleansedKey = schoolName + "_" + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_uncleansed"
                s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=uncleansedKey, Body=serializedData)
            
                print('uncleansed stored')
                await curator.updateUncleansed(uncleansedKey, schoolName)
                cleansedData = await task['cleanse'](uncleansedKey)
                serializedCleansedData = json.dumps(cleansedData)
                cleansedKey = schoolName + "_" + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_cleansed"
                
                # store cleansed
                print("storing cleansed")
                s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=cleansedKey, Body=serializedCleansedData)
            else:
                cleansedKey = schoolName + "_" + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_cleansed"
                print(f"storing data {cleansedKey}")
                s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=cleansedKey, Body=serializedData)
            
            print('cleansed stored')
            await curator.updateCleansed(cleansedKey, schoolName)
            with open('sfu-data.json', 'w') as f:
                json.dump(cleansedData, f)
        except:
            return

# for testing
asyncio.run(runTasks())
        
