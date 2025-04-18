
# Basic Imports
import pandas as pd
import time
import traceback
import json

# BeautifulSoup
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver

# Import classes from folder
from app.record_data import RecordData
from app.scrape import Scrape


class Processor:
    """
    Designed to distribute the task and start the process.
    """
    def __init__(self, website_address: str, folder_location: str):
        self.website_address = website_address
        self.folder_location = folder_location
        self.driver = webdriver.Chrome()

    def initialize_gathering(self, *args):
        """
        Initiate the process of scraping with specified arguments.
            args: Arguments to specify the range of pages to scrape.
        """
        try:

            # calling classes
            record = RecordData(self.folder_location)
            scrape = Scrape(self.website_address, self.folder_location)

            # Display info on terminal and write in log
            with open('version.json', 'r') as f:
                version_info = json.load(f)
                major = version_info["major"]
                minor = version_info["minor"]
                patch = version_info["patch"]
                release = version_info["release"]
                description = version_info["description"]

                record.create_log('INFO', f'Version: {major}.{minor}.{patch}-{release}')
                record.create_log('INFO', f'Version: {description}')

            record.create_log('INFO', 'Page is loading...')
            # Initializing web driver
            self.driver.get(self.website_address)
            time.sleep(3)

            # Initiate soup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # Track number of results
            num_result_block = soup.find("a", id="tab-restaurants-active")
            num_restults = num_result_block.find("span").text.replace("(", "").replace(")","")

            # Track number of pages
            num_pages = soup.find("div", class_="mb0 mt40 color-dark bold fs-16 text-center p10").text.split()[-1].strip()
            # Saving infon into log
            record.create_log('INFO', 'Started')
            record.create_log('INFO' , f'Number of result(s) for scraping {num_restults}')
            record.create_log('INFO', f'Number of page(s) for scraping {num_pages}')

            # Process args for instructions
            for item in args:
                if isinstance(item, str):
                    if item == "all":
                        scrape.get_page(1, int(num_pages) + 1)

                if isinstance(item, (list, tuple)):
                    if len(item) == 1:
                        scrape.get_page(1, item[0])
                    elif len(item) == 2:
                        scrape.get_page(item[0], item[1] + 1)
                    else:
                        scrape.get_page(0, 0, item)

                if isinstance(item, int):
                    scrape.get_page(0 , 0, [item])

        except Exception:
            full_trace = traceback.format_exc()
            record.create_log('ERROR', full_trace)
            record.create_log('WARNING', 'Scraping process interupted no record was made.')
