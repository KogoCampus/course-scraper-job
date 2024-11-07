

async def createSection(sectionName ="", deliveryMethod="", term="", activity="", credits="", startDate=[], startTime=[], endDate=[], endTime=[], days=[]):
    sections = {
        "sectionName": sectionName, 
        "deliveryMethod": deliveryMethod, 
        "term": term, 
        "activity": activity, 
        "credits": credits,
        "startDate": startDate, 
        "startTime": startTime, 
        "endDate": endDate, 
        "endTime": endTime,
        "days": days
    }

    return sections

async def createCourse(courseName="", courseCode="", sections=[]):
    course = {
        "courseName": courseName,
        "courseCode": courseCode,
        "sections": sections,
    }

    return course

async def createProgram(programName="", programCode="", courses=[]):
    program = {
        "programName": programName,
        "programCode": programCode,
        "courses": courses,
    }

    return program
