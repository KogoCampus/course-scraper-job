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
        "function": sfuScraper.extractData
    },
    {
        "schoolName": "university_of_british_columbia",
        "function": ubcScraper.getAllData
    }
]

async def run():
    for task in schoolToScraper:
        schoolName = task['schoolname']
        f = task['function']

        # data: dict
        data = asyncio.run(f())

        # store uncleansed
        s3 = boto3.client('s3')
        load_dotenv()
        serializedData = json.dumps(data)
        uncleansedKey = schoolName + str(datetime.now().month) + "_" + str(datetime.now().day) + "_uncleansed"
        try:
            s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=uncleansedKey, Body=serializedData)
            curator.updateUncleansed(uncleansedKey, schoolName)

            # cleanse
            cleansedData = json.dumps(cleanseSFU(uncleansedKey))
            cleansedKey = schoolName + str(datetime.now().month) + "_" + str(datetime.now().day) + "_cleansed"

            # store cleansed
            s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=cleansedKey, Body=cleansedData)
            curator.updateCleansed(cleansedKey, schoolName)
        except:
            return
        
        
