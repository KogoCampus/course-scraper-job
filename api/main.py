import boto3
from dotenv import load_dotenv
from fastapi import FastAPI
import os
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# schoolName = simon_fraser_university
@app.get("/courses/{schoolName}")
async def getAllCourses(schoolName):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)

    s3 = boto3.client('s3')
    load_dotenv()
    record = json.loads(f)
    if record.get(schoolName):
        key = record[schoolName]['latest_scraped_data_id_cleansed']
        if key:
            response = s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=key)
            obj = {
                "schoolName": schoolName,
                "updateDate": key,
                "data": response
            }
            return json.dumps(obj)
        
    return json.dumps(
        {
            "error": "no data found"
        }
    )



@app.get("/courses/{schoolName}/{dpt}")
async def getAllCoursesByDepartment(schoolName, dpt):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)

    s3 = boto3.client('s3')
    load_dotenv()
    record = json.loads(f)
    if record.get(schoolName):
        key = record[schoolName]['latest_scraped_data_id_cleansed']
        if key:
            response = json.loads(s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=key)['Body'].read())
            for subject in response:
                if subject['programCode'] == dpt:
                    obj = {
                        "schoolName": schoolName,
                        "updateDate": key,
                        "data": subject
                    }
                    return json.dumps(obj)
    return json.dumps(
        {
            "error": "no data found"
        }
    )

@app.get("/courses/{schoolName}/{dpt}/{cid}")
async def getAllCoursesByCourseId(schoolName, dpt, cid):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)

    s3 = boto3.client('s3')
    load_dotenv()
    record = json.loads(f)
    if record.get(schoolName):
        key = record[schoolName]['latest_scraped_data_id_cleansed']
        if key:
            response = json.loads(s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=key)['Body'].read())
            for subject in response:
                if subject['programCode'] == dpt:
                    for course in subject['courses']:
                        if course['courseCode'].split(' ')[1] == cid:
                            obj = {
                                "schoolName": schoolName,
                                "updateDate": key,
                                "data": course
                            }
                            return json.dumps(obj)
    return json.dumps(
        {
            "error": "no data found"
        }
    )

@app.get("/courses/{schoolName}/{dpt}/{cid}/{sid}")
async def getAllCoursesBySectionId(schoolName, dpt, cid, sid):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)

    s3 = boto3.client('s3')
    load_dotenv()
    record = json.loads(f)
    if record.get(schoolName):
        key = record[schoolName]['latest_scraped_data_id_cleansed']
        if key:
            response = json.loads(s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=key)['Body'].read())
            for subject in response:
                if subject['programCode'] == dpt:
                    for course in subject['courses']:
                        if course['courseCode'].split(' ')[1] == cid:
                            for section in course['sections']:
                                if section['sectionName'].split(' ')[2] == sid:
                                    obj = {
                                        "schoolName": schoolName,
                                        "updateDate": key,
                                        "data": section
                                    }
                                    return json.dumps(obj)
    return json.dumps(
        {
            "error": "no data found"
        }
    )


