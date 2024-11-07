from playwright.async_api import async_playwright
from parser import prompter
import json

data = []

async def setupPage(page):
    # selecting options (terms and campus location)
    await page.wait_for_selector('.m-menu-toggle')
    await page.locator('.m-menu-toggle').click()

    await page.wait_for_selector('.menu-campus-session__tab-btn')

    await page.locator('.menu-campus-session__tab-btn:nth-of-type(2)').click()

    await page.locator('.menu-campus-session__menu-link:nth-of-type(3)').click()

    await page.wait_for_selector('#subjects-table td')

async def getAllData(url = "https://courses.students.ubc.ca/browse-courses"):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({
            "width": 500,
            "height": 800,
        })
        await page.goto(url)
        await setupPage(page)

        failed = []
        await page.wait_for_selector('#subjects-table')

        firstName = await page.evaluate("""async () => {
            return document.querySelector('td[data-colindex="0"] a').textContent                                                        
        }""")

        prevName = ""

        stop = False
        i = 0

        while(not stop):
            if i != 0:
                await page.wait_for_selector('main')
                await page.locator('#pagination-next').click()

            print(f'Page {i+1}')
            subjects = await page.locator('td[data-colindex="0"] a').all()

            for j in range(0, len(subjects), 1):
                currentName = await subjects[j].inner_text()
                print(currentName)
                if currentName != prevName:
                    prevName = currentName
                    await subjects[j].click()

                    try:
                        await page.wait_for_selector('.subjects-courses', timeout=20000)
                    except:
                        print(f"{currentName} reload")
                        failed.append(currentName)

                    currentProgram = {
                        "programName": "",
                        "programCode": "",
                        "courses": [],
                    }
                    
                    await page.query_selector('.subjects-courses')
                    currentCode = await (await page.query_selector('.l-node h1')).inner_html()
                    currentProgram['programName'] = currentName
                    currentProgram['programCode'] = currentCode.split('-', 1)[1].strip()
                    currentCourse = {
                        "courseName": "",
                        "courseCode": "",
                        "sections": []
                    }

                    courses = await page.locator('td[data-colindex="0"] a').all()
                    for k in courses:
                        await k.click()
                        await page.wait_for_selector('.course-view')
                        currentCourse = {
                            "courseName": "",
                            "courseCode": "",
                            "sections": []
                        }

                        courseName = await (await page.query_selector('.l-node__title')).inner_text()
                        currentCourse['courseCode'] = courseName.split('-', 1)[0].strip()
                        currentCourse['courseName'] = courseName.split('-', 1)[1].strip()
                        html = await page.query_selector('.course-view__tables')
                        if html:
                            sections = await page.locator('.course-sections-box').all()
                            for s in sections:
                                section = await s.inner_html()
                                out = await prompter.extractData(section)
                                currentCourse['sections'].extend(out)

                        # print(currentCourse)    
                        currentProgram['courses'].append(currentCourse)
                        await page.go_back()
                        courses = await page.locator('td[data-colindex="0"] a').all()
                    
                    await page.go_back()
                    data.append(currentProgram)
                    await page.wait_for_selector('td[data-colindex="0"] a')
                    isFirstPage = await page.evaluate("""
                        async () => {
                            return document.querySelector('td[data-colindex="0"] a').textContent
                        }
                    """)
                    
                    if isFirstPage == firstName and i != 0:
                        await page.goto(url)
                        await setupPage(page)
                        for x in range(0, i):
                            await page.wait_for_selector('#subjects-table')
                            await page.locator('#pagination-next').click()
                    
                    await page.wait_for_selector('td[data-colindex="0"] a')
                    subjects = await page.locator('td[data-colindex="0"] a').all()
            
            i += 1
            pageNumber = (await (await page.query_selector('tfoot p')).inner_text()).split('-')[1].split(' ')
            if pageNumber[0] == pageNumber[2]:
                stop = True
            courseName = await (await page.query_selector('.l-node__title')).inner_text()

        await browser.close()

        # data = json.dumps(data)
        with open('ubc-data.json', 'w') as f:
            json.dump(data, f)

        return data

# asyncio.run(getAllData("https://courses.students.ubc.ca/browse-courses"))