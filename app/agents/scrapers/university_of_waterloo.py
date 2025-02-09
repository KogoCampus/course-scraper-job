import asyncio
from datetime import datetime
import json
from playwright.async_api import async_playwright
import logging

from .base import BaseScraper
from app.models.course import CourseListingModel


class UniversityOfWaterlooScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.base_url = "https://classes.uwaterloo.ca/under.html" #Automatically selects the current term.
        self.data = []
    
    async def fetch_courses(self) -> CourseListingModel:
        async with async_playwright() as p:
            #i.e. chrome
            browser = await p.chromium.launch()
            #i.e. page
            page = await browser.new_page()
            await page.set_viewport_size({
                "width": 500,
                "height": 800,
            })
            #i.e. go to that url
            await page.goto(self.base_url)
            await page.wait_for_selector("#ssubject option")
            programs = await page.locator("#ssubject > option:nth-child(2)")

            for i in programs:
                await i.click()
                await page.locator("body > main > form > p:nth-child(12) > input[type=submit]:nth-child(1)").click() #search
                #Checks if there exists a table on the page
                try:
                    await page.wait_for_selector("body > main > p:nth-child(3) > table")
                except:
                    await page.go_back()
                    continue
                program = {
                    "programName": await i.inner_text(),
                    "programCode": "",
                    "courses": []
                    }
                print(await i.inner_text())
                self.data.append() #extend?
        return self.data