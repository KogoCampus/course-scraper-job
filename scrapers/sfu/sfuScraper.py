from datetime import datetime
import requests
import json
from converter import *

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
        currentProgram = await createProgram(d['name'], d['text'], [])
        print(d['name'])
        courses = requests.get(baseUrl + "/" + d['value']).json()
        if "errorMessage" not in courses:
            for c in courses:
                currentCourse = await createCourse(c['title'], currentProgram['programCode'] + " " + c['text'], [])
                sections = requests.get(baseUrl + "/" + d['value'] + "/" + c['value']).json()
                if "errorMessage" not in sections:
                    for s in sections:
                        detail = requests.get(baseUrl + "/" + d['value'] + "/" + c['value'] + "/" + s['value']).json()
                        
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
                            cs['startDate'].append(block['startDate'])
                            cs['endDate'].append(block['endDate'])
                            cs['startTime'].append(block['startTime'] if block.get('startTime') else "")
                            cs['endTime'].append(block['endTime'] if block.get('endTime') else "")
                            cs['days'].append(block['days'])
                        
                        currentSection = await createSection(
                            sectionName=info['name'],
                            deliveryMethod=info['deliveryMethod'] if info.get('deliveryMethod') else "", 
                            term=info['term'],
                            activity=courseSchedule[0]['sectionCode'] if courseSchedule else "", 
                            credits=info['units'] if info.get('units') else "", 
                            startDate=cs['startDate'],
                            startTime=cs['startTime'],
                            endDate=cs['endDate'],
                            endTime=cs['endTime'],
                            days=cs['days'],
                        )
                        
                        
                        currentCourse['sections'].append(currentSection)
                        print(f'CS: {currentSection}')
                        # print('\n')
                
                currentProgram['courses'].append(currentCourse)
                # print(json.dumps(currentProgram))
        data.append(currentProgram)

    # temporary
    with open('sfu-data.json', 'w') as f:
        json.dump(data, f)

    return data

# asyncio.run(extractData())