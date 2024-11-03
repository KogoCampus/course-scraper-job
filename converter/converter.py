import json
import os
import boto3
from dotenv import load_dotenv

# key should be "simon-fraser-university-2024-10-29-uncleansed"
async def cleanseSFU(key):
    print(f'cleansing data for {key}')
    s3 = boto3.client('s3')
    load_dotenv()
    response = s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=key)
    content = json.loads(response['Body'].read())

    for subject in content:
        for course in subject['courses']:
            sections = []
            for detail in course['sections']:
                info = detail['info']
                courseSchedule = detail['courseSchedule'] if detail.get('courseSchedule') else []
                
                currentSection = {
                    "sectionName": "", 
                    "deliveryMethod": "", 
                    "term": "", 
                    "activity": "", 
                    "credits": "",
                    "startDate": [], 
                    "startTime": [], 
                    "endDate": [], 
                    "endTime": [], 
                    "days": []
                }

                cs = {
                    "activity": [],
                    "startDate": [],
                    "endDate": [],
                    "startTime": [],
                    "endTime": [],
                    "days": []
                }

                for block in courseSchedule:
                    cs['startDate'].append(block['startDate'])
                    cs['endDate'].append(block['endDate'])
                    cs['startTime'].append(block['startTime'] if block.get('startTime') else "")
                    cs['endTime'].append(block['endTime'] if block.get('endTime') else "")
                    cs['days'].append(block['days'])

                currentSection = {
                    "sectionName": info['name'], 
                    "deliveryMethod": info['deliveryMethod'] if info.get('deliveryMethod') else "", 
                    "term": info['term'], 
                    "activity": courseSchedule[0]['sectionCode'] if courseSchedule else "", 
                    "credits": info['units'] if info.get('units') else "", 
                    "startDate": cs['startDate'], 
                    "startTime": cs['startTime'], 
                    "endDate": cs['endDate'], 
                    "endTime": cs["endTime"], 
                    "days": cs['days']
                }

                sections.append(currentSection)

            course['sections'] = sections

    # print(json.dumps(content))
    return content
                    






