import json
import os
import boto3
from dotenv import load_dotenv

# key should be "simon-fraser-university-2024-10-29-uncleansed"
async def cleanseSFU(key):
    s3 = boto3.client('s3')
    load_dotenv()
    response = s3.get_object(Bucket=os.getenv('S3_BUCKET', key))
    content = json.loads(response['Body'].read())

    for subject in content:
        for course in subject['courses']:
            for detail in course['detail']:
                info = detail['info']
                courseSchedule = detail['courseSchedule'] if detail.get('courseSchedule') else []
                cs = {
                    "activity": [],
                    "startDate": [],
                    "endDate": [],
                    "startTime": [],
                    "endTime": [],
                    "days": []
                }

                for block in courseSchedule:
                    cs['activity'].append(block['sectionCode'])
                    cs['startDate'].append(block['startDate'])
                    cs['endDate'].append(block['endDate'])
                    cs['startTime'].append(block['startTime'] if block.get('startTime') else "")
                    cs['endTime'].append(block['endTime'] if block.get('endTime') else "")
                    cs['days'].append(block['days'])


                currentSection = {
                    "sectionName": info['name'], 
                    "deliveryMethod": info['deliveryMethod'], 
                    "term": info['term'], 
                    "activity": cs['activity'], 
                    "credits": info['units'] if info.get('units') else "", 
                    "startDate": cs['startDate'], 
                    "startTime": cs['startTime'], 
                    "endDate": cs['endDate'], 
                    "endTime": cs["endTime"], 
                    "days": cs['days']
                }

                course['detail'] = currentSection

    return content
                    






