from datetime import datetime
import asyncio
import boto3
import requests
import json
import os
from dotenv import load_dotenv
import curator

data = []

async def extractData():
    month = datetime.now().month
    year = datetime.now().year
    term = ""

    if month >= 1 and month <= 4:
        term = "spring"
    elif month <= 8 and month >= 5:
        term = "summer"
    elif (month >= 9 and month <= 12):
        term = "fall"
    else:
        raise Exception("Invalid term")

    baseUrl = "https://www.sfu.ca/bin/wcm/course-outlines?" + str(year) + "/" + term

    dpt = requests.get(baseUrl).json()

    for d in dpt:
        if not d.get('name'):
            continue
    
        currentSubject = {
            "programName": d['name'],
            "programCode": d['text'],
            "courses": [],
        }
        print(d['name'])
        courses = requests.get(baseUrl + "/" + d['value']).json()
        if "errorMessage" not in courses:
            for c in courses:
                currentCourse = {
                    "courseName": c['title'],
                    "courseCode": currentSubject['programCode'] + " " + c['text'],
                    "sections": [],
                }
                sections = requests.get(baseUrl + "/" + d['value'] + "/" + c['value']).json()
                if "errorMessage" not in sections:
                    for s in sections:
                        section = requests.get(baseUrl + "/" + d['value'] + "/" + c['value'] + "/" + s['value']).json()
                        currentCourse['sections'].append(section)
                        # print(f'CS: {currentSection}')
                        # print('\n')
                
                currentSubject['courses'].append(currentCourse)
                # print(json.dumps(currentSubject))
        data.append(currentSubject)

    # temporary
    with open('sfu-data.json', 'w') as f:
        json.dump(data, f)

    return data

# asyncio.run(extractData())

# kogo-campus-crawler-staging-data:
#     simon_fraser_university_2024_10_29_uncleansed: {
#         ...
#     },
#     simon_fraser_university_2024_10_29_cleansed: {
#         ...
#     },
#     simon_fraser_university_2024_10_15_cleansed: {
#         ...
#     },
#     university_of_british_columbia_2024_10_22_uncleansed: {
#         ...
#     },
