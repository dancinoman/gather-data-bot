
# Basic Imports
from dotenv import load_dotenv
import pandas as pd
import time
import datetime
import traceback
import json

# Selenium imports
from selenium import webdriver

# BeautifulSoup
from bs4 import BeautifulSoup

# Import classes from folder
from app.record_data import RecordData
from app.scrape import Scrape

# Load environment variablesgit pyen
load_dotenv()


class Processor:

    hour = datetime.datetime.now().strftime('%H:%M:%S')
    id = 1
    all_log_txt = []

    driver = webdriver.Chrome()
    start_time = time.time()

    def __init__(self, website_address: str, folder_location: str):
        self.website_address = website_address
        self.folder_location = folder_location

    def initialize_gathering(self, *args):

        try:

            # calling classes
            record = RecordData(self.folder_location)

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
                        self.get_data(1, int(num_pages) + 1)

                if isinstance(item, (list, tuple)):
                    if len(item) == 1:
                        self.get_data(1, item[0])
                    elif len(item) == 2:
                        self.get_data(item[0], item[1] + 1)
                    else:
                        self.get_data(0, 0, item)

                if isinstance(item, int):
                    self.get_data(0 , 0, [item])

        except Exception:
            full_trace = traceback.format_exc()
            record.create_log('ERROR', full_trace)
            record.create_log('WARNING', 'Scraping process interupted no record was made.')


    def get_data(self, min_page: int, max_page: int, pages = None):

        # calling classes
        record = RecordData(self.folder_location)
        scrape_frame = Scrape()
        # Scrape by page
        def execute_scrape(page_num):

            # Start scraping content to the instruction page
            web_link = self.website_address + f"&page={page_num}#{page_num}"
            self.driver.get(web_link)
            time.sleep(3)

            #Using beautiful soup to get the list of restaurants
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            resto_block = soup.find_all("div", class_='search-result')

            record.create_log('INFO', f'Starting to fetch on page {page_num}')

            # Scrape all content block

            for resto in resto_block:
                try:
                    # Get cover content and return unique page link
                    unique_page = scrape_frame.cover_content(resto, self.id)

                    # Go to unique page details to get more info
                    self.driver.get(unique_page)
                    time.sleep(3)
                    all_info = scrape_frame.individual_content(self.driver.page_source, self.id)

                    # Store to CSV
                    record.save_csv(*all_info)
                    record.create_log('INFO', f'#{len(scrape_frame.restaurants)} - {scrape_frame.restaurants[-1]["name"]} recorded')

                    #Prepare for next loop
                    self.id += 1
                    # Stop if reached the last page
                    if page_num == max_page+ 1:
                        self.create_log('INFO', "Bot's task completed")
                        break

                except Exception:
                    full_trace = traceback.format_exc()
                    record.create_log('ERROR', full_trace)
                    record.create_log('INFO', f"Got issue with id: {self.id}")
                    self.id += 1
                    continue

        # Execute a range or list of page
        if max_page != 0:

            for page_num in range(min_page, max_page):
                execute_scrape(page_num)

        elif pages is not None:
            for page in pages:
                execute_scrape(page)
