from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/courses/{schoolName}")
async def getAllCourses():
    return {"message": "Hello World"}

@app.get("/courses/{schoolName}/{dpt}")
async def getAllCoursesByDepartment():
    return {"message": "Hello World"}

@app.get("/courses/{schoolName}/{dpt}/{cid}")
async def getAllCoursesByCourseId():
    return {"message": "Hello World"}

@app.get("/courses/{schoolName}/{dpt}/{cid}/{sid}")
async def getAllCoursesBySectionId():
    return {"message": "Hello World"}


