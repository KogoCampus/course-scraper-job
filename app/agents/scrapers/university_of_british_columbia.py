from datetime import datetime
import json
from playwright.async_api import async_playwright
import logging

from .base import BaseScraper
from app.models.course import CourseListingModel


class UniversityOfBritishColumbiaScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.base_url = "https://courses.students.ubc.ca/browse-courses"
        self.data = []

    def _determine_term(self) -> str:
        """Determine current term based on date"""
        month = datetime.now().month
        
        if 1 <= month <= 4:
            return "Winter"
        elif 5 <= month <= 8:
            return "Summer"
        else:  # 9 <= month <= 12
            return "Winter"  # UBC uses Winter for Fall term
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

        for x in range(0, pageNum):
            await page.wait_for_selector('#subjects-table')
            await page.locator('#pagination-next').click()

    async def fetch_courses_in_page(self, page, pageNum: int = 0):
        """Fetch course data for a specific page"""
        await self.setupPage(page, pageNum)
        failed = []
        await page.wait_for_selector('#subjects-table')

        firstName = await page.evaluate("""async () => {
            return document.querySelector('td[data-colindex="0"] a').textContent                                                        
        }""")

        prevName = ""
        self.logger.info(f'Page {pageNum + 1}')
        subjects = await page.locator('td[data-colindex="0"] a').all()

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
                for k in courses:
                    await k.click()
                    await page.wait_for_selector('.course-view')
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
                        for s in sessions:
                            session = await s.inner_html()
                            if sessionIndex == 0:
                                prompts = [
                                    "Parse this HTML section into a list of course sessions. Each session should have:",
                                    "- sessionName: The section code/name (e.g., 'L1A', 'LAB 2', etc.)",
                                    "- sessionType: The activity of the section (e.g., 'Lecture' or 'Seminar' or 'Thesis' or 'Independent Study', etc)"
                                    "- campus: This value must always be 'Vancouver'",
                                    "- location: The room/building location (null if not available)",
                                    "- schedules: A list of schedule objects, each containing:",
                                    "  - days: List of days as ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']",
                                    "  - startTime: Unix timestamp for start time (null if not available)",
                                    "  - endTime: Unix timestamp for end time (null if not available)",
                                    "- childSession: An empty list"
                                ]
                            else:
                                prompts = [
                                    "Parse this HTML section into a list of course sessions. If sessionType is 'Lecture' or 'Seminar' or 'Thesis' or 'Independent Study', each session should have:",
                                    "- sessionName: The section code/name (e.g., 'L1A', 'LAB 2', etc.)",
                                    "- sessionType: The activity of the section (e.g., 'Lecture' or 'Seminar' or 'Thesis' or 'Independent Study')"
                                    "- campus: This value must always be 'Vancouver'",
                                    "- location: The room/building location (null if not available)",
                                    "- schedules: A list of schedule objects, each containing:",
                                    "  - days: List of days as ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']",
                                    "  - startTime: Unix timestamp for start time (null if not available)",
                                    "  - endTime: Unix timestamp for end time (null if not available)",
                                    "- childSession: An empty list"
                                    "If sessionType is other than 'Lecture' or 'Seminar' or 'Thesis' or 'Independent Study',",
                                    "change'sessionName' to 'childSessionName' and 'sessionType' must be 'childSessionType'",
                                    "and no need for childSession",
                                ]
                            out = await self.llm_html_parser.parse_html_to_json_list(session, prompts)
                            self.logger.info(out)
                            if "childSessionName" in out[0]:
                                for s in currentCourse.get('sessions'):
                                    if "sessionName" in s:
                                        self.logger.info(s)
                                        s['childSession'].extend(out)
                            else:
                                currentCourse['sessions'].extend(out)
                            sessionIndex += 1

                    currentProgram['courses'].append(currentCourse)
                    await page.go_back()
                    courses = await page.locator('td[data-colindex="0"] a').all()
                
                await page.go_back()
                self.data.append(currentProgram)
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

    async def fetch_courses(self) -> CourseListingModel:
        """Fetch course data from UBC API"""
        year = datetime.now().year
        term = self._determine_term()
        
        self.logger.info(f"=== Start UBC scraper for {term} {year} ===")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_viewport_size({
                "width": 500,
                "height": 800,
            })
            await page.goto(self.base_url)
            
            # Get total number of pages
            # await self.setupPage(page, 0)
            # await page.wait_for_selector('tfoot p')
            # page_info = await page.locator('tfoot p').inner_text()
            # total_pages = int(page_info.split()[-1])
            # 
            # # Create list of page numbers to process
            # pages = list(range(total_pages))
            # 
            # # Define the page processing function
            # async def process_page(page_num: int) -> None:
            #     async with async_playwright() as p:
            #         browser = await p.chromium.launch()
            #         page = await browser.new_page()
            #         await page.set_viewport_size({
            #             "width": 500,
            #             "height": 800,
            #         })
            #         await page.goto(self.base_url)
            #         await self.fetch_courses_in_page(page, page_num)
            #         await browser.close()
            # 
            # # Process pages using sliding window
            # from app.utils.async_utils import sliding_window_request
            # await sliding_window_request(
            #     items=pages,
            #     task_fn=process_page,
            #     window_size=3,  # Process 3 pages at a time
            #     delay_between_windows=1  # Wait 1 second between windows
            # )

        return {
            "semester": f"{term} {year}",
            "programs": self.data,
            "total_programs": len(self.data),
            "total_courses": sum(len(program["courses"]) for program in self.data),
            "total_sections": sum(
                len(course["sessions"]) 
                for program in self.data 
                for course in program["courses"]
            )
        } 