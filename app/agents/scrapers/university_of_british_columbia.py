import asyncio
from datetime import datetime
import json
from playwright.async_api import async_playwright
import logging

import pytz

from .base import BaseScraper
from app.models.course import (CourseListingModel, Day)


class UniversityOfBritishColumbiaScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.base_url = "https://courses.students.ubc.ca/browse-courses"
        self.totalPrograms = 0
        self.totalCourses = 0
        self.totalSections = 0

    def _determine_term(self) -> str:
        """Determine current term based on date"""
        month = datetime.now().month
        
        if 1 <= month <= 4:
            return "Winter 2"
        elif 5 <= month <= 8:
            return "Summer"
        else:  # 9 <= month <= 12
            return "Winter 1"  # UBC uses Winter for Fall term
        return "SampleTerm"
    
    async def setupPage(self, page, pageNum):
        # selecting options (terms and campus location)
        await page.wait_for_selector('.m-menu-toggle')
        await page.locator('.m-menu-toggle').click()

        await page.wait_for_selector('.menu-campus-session__tab-btn')

        # select sem
        await page.locator('.menu-campus-session__tab-btn:nth-of-type(2)').click()
        
        # 1 - up-upcoming sem
        # 2 - upcoming sem
        # 3 - current sem
        # 4 - prev sem
        await page.locator('.menu-campus-session__menu-link:nth-of-type(3)').click()

        await page.wait_for_selector('#subjects-table td')

        for x in range(pageNum):
            await page.wait_for_selector('#subjects-table')
            await page.locator('#pagination-next').click()
    
    async def setDays(self, days_str):
        if days_str == '':
            return None
        day_map = {
            'Monday': Day.MONDAY,
            'Tuesday': Day.TUESDAY,
            'Wednesday': Day.WEDNESDAY,
            'Thursday': Day.THURSDAY,
            'Friday': Day.FRIDAY,
            'Saturday': Day.SATURDAY,
            'Sunday': Day.SUNDAY
        }
        days_str = days_str.split(', ')
        days = []
        for day in days_str:
            if day in day_map:
                days.append(day_map[day].value)
        return days

    async def setTime(self, date, time):
        pst_tz = pytz.timezone('America/Vancouver')
        if await time.inner_html() == '':
            return None
        converted_date = datetime.strptime(await date.inner_html(), '%Y-%m-%d').date()
        converted_time = datetime.strptime(await time.inner_html(), '%H:%M').time()
        dt = datetime.combine(converted_date, converted_time)
        dt_tz = pst_tz.localize(dt)
        return int(dt_tz.timestamp())

    async def fetch_courses(self) -> CourseListingModel:
        r = []
        len = 0
        window = 1

        async with async_playwright() as p:
            browser = await p.firefox.launch()
            page = await browser.new_page()
            await page.set_viewport_size({
                "width": 500,
                "height": 800,
            })

            page.set_default_timeout = 60000
            page.set_default_navigation_timeout = 60000

            await page.goto(self.base_url)
            await page.wait_for_selector('#subjects-table')
            pagination = (await page.locator('.MuiTablePagination-displayedRows').inner_html()).split(' of')
            subjectLen = int(pagination[0].split('-')[1].strip())
            totalSubjectLen = int(pagination[1].strip())
            len = int(totalSubjectLen / subjectLen) + 1
            itr = int(len / window)
            remainder = len % window

            # r = await asyncio.gather(*([asyncio.ensure_future(self.fetch_courses_e(page=page, pageNum=u)) for u in range(0,len)]))

            for i in range(window, len + window - 1, window):
                r.append(await asyncio.gather(*([asyncio.ensure_future(self.fetch_courses_e(pageNum=u)) for u in range(i-window,i)])))
            
            r.append(await asyncio.gather(*([asyncio.ensure_future(self.fetch_courses_e(pageNum=u+(window*itr))) for u in range(remainder)])))

            await page.close()
            await browser.close()
        
        year = datetime.now().year
        term = self._determine_term()
        
        data = {
            "semester": f"{term} {year}",
            "programs": r,
            "total_programs": self.totalPrograms,
            "total_courses": self.totalCourses,
            "total_sections": self.totalSections
        }

        # for d in r:
        #     data['semester'] = d['semester']
        #     data['programs'].extend(d['programs'])
        #     data['total_programs'] += d['total_programs']
        #     data['total_courses'] += d['total_courses']
        #     data['total_sections'] += d['total_sections']
        
        return data


    async def fetch_courses_e(self, pageNum) -> CourseListingModel:
        """Fetch course data from UBC API"""
        year = datetime.now().year
        term = self._determine_term()
        lecture_types = ['Lecture', 'Seminar', 'Independent Study', 'Thesis']
        
        self.logger.info(f"=== Start UBC scraper for {term} {year} in page {pageNum + 1} ===")
        
        # retrieve each html page for courses from ubc website
        # https://github.com/KogoCampus/course-scraper-job/blob/dff5418512899a57492d697a596f9a6ab477ebf9/scrapers/ubc/ubcScraper.py

        # parse each html page into json using self.llm_html_parser
        async with async_playwright() as p2:
            browser = await p2.webkit.launch()
            page = await browser.new_page()
            await page.set_viewport_size({
                "width": 500,
                "height": 800,
            })

            page.set_default_timeout = 60000
            page.set_default_navigation_timeout = 60000

            await page.goto(self.base_url)
            await self.setupPage(page, pageNum)

            failed = []
            await page.wait_for_selector('#subjects-table')

            firstName = await page.evaluate("""async () => {
                return document.querySelector('td[data-colindex="0"] a').textContent                                                        
            }""")

            prevName = ""

            subjects = await page.locator('td[data-colindex="0"] a').all()

            res = []
            self.totalPrograms += len(subjects)

            for j in range(0, len(subjects), 1):
                currentName = await subjects[j].inner_text()
                self.logger.info(currentName)
                
                if currentName != prevName:
                    prevName = currentName
                    await subjects[j].click()
                    try:
                        await page.wait_for_selector('.subjects-courses', timeout=20000)
                    except:
                        self.logger.info(f"{currentName} reload")
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
                        "sessions": []
                    }

                    courses = await page.locator('td[data-colindex="0"] a').all()
                    self.totalCourses += len(courses)
                    for k in courses:
                        try:
                            await k.click()
                            await page.wait_for_selector('.course-view')
                        except:
                            self.logger.info(f"A section in {currentName} failed")
                            break

                        currentCourse = {
                            "courseName": "",
                            "courseCode": "",
                            "credit": 0,
                            "sessions": []
                        }

                        courseName = await (await page.query_selector('.l-node__title')).inner_text()
                        credit = await (await page.query_selector('.course-view__detail-title')).inner_text()
                        currentCourse['credit'] = credit.split('-')[1].strip()
                        currentCourse['courseCode'] = courseName.split('-', 1)[0].strip()
                        currentCourse['courseName'] = courseName.split('-', 1)[1].strip()
                        html = await page.query_selector('.course-view__tables')
                        if html:
                            sessions = await page.locator('.course-sections-box').all()
                            sessionIndex = 0
                            self.totalSections += len(sessions)
                            for s in range(1, len(sessions)+1):
                                data = await page.locator(f'.course-sections-box:nth-of-type({s}) p').all()
                                
                                converted_days = await self.setDays(await data[8].inner_html())
                                converted_startTime = await self.setTime(data[6], data[7])
                                converted_endTime = await self.setTime(data[9], data[10])
                                if await data[4].inner_html() in lecture_types:
                                    out = [
                                        {
                                            'sessionName': await data[0].text_content(),
                                            'sessionType': await data[4].inner_html(),
                                            'campus': 'Vancouver',
                                            'location': None,
                                            'schedules': [
                                                {
                                                    'days': converted_days,
                                                    'startTime': converted_startTime,
                                                    'endTime': converted_endTime
                                                }
                                            ],
                                            'childSession': []
                                        }
                                    ]
                                else:
                                    out = [
                                        {
                                            'childSessionName': await data[0].text_content(),
                                            'childSessionType': await data[4].inner_html(),
                                            'campus': 'Vancouver',
                                            'location': None,
                                            'schedules': [
                                                {
                                                    'days': converted_days,
                                                    'startTime': converted_startTime,
                                                    'endTime': converted_endTime
                                                }
                                            ]
                                        }
                                    ]

                                if "childSessionName" in out[0]:
                                    for s in currentCourse.get('sessions'):
                                        if "sessionName" in s:
                                            s['childSession'].extend(out)
                                else:
                                    currentCourse['sessions'].extend(out)
                                sessionIndex += 1
                        currentProgram['courses'].append(currentCourse)
                        await page.go_back()
                        courses = await page.locator('td[data-colindex="0"] a').all()
                    
                    await page.go_back()
                    res.append(currentProgram)
                    await page.wait_for_selector('td[data-colindex="0"] a')
                    isFirstPage = await page.evaluate("""
                        async () => {
                            return document.querySelector('td[data-colindex="0"] a').textContent
                        }
                    """)
                    if isFirstPage != firstName and pageNum != 0:
                        await page.goto(self.base_url)
                        await self.setupPage(page, pageNum)
                    
                    await page.wait_for_selector('td[data-colindex="0"] a')
                    subjects = await page.locator('td[data-colindex="0"] a').all()

                pageNumber = (await (await page.query_selector('tfoot p')).inner_text()).split('-')[1].split(' ')
                if pageNumber[0] == pageNumber[2]:
                    stop = True
                courseName = await (await page.query_selector('.l-node__title')).inner_text()
                
            await page.close()
            await browser.close()

        # return data in foramt of models/course.py

        return res