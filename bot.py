# Basic Imports
import os
import requests
import pandas as pd
import csv
import time
import datetime
import re
import traceback
import json

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as ec
import chromedriver_binary

# BeautifulSoup
from bs4 import BeautifulSoup
import bs4

#TODO fix when only one element used with a list to indicate the number of page
#TODO fix when an int is used to indicate the number of page instead is used to indicate the number of restaurant to scrape
#TODO fix no longer use webdriver
#TODO generate new data filename differently
class GatherData:

    date = datetime.date.today().strftime('%d-%m-%Y')
    hour = datetime.datetime.now().strftime('%H:%M:%S')
    data_source = "https://www.restomontreal.ca/s/?restaurants=greater-montreal&lang=en"
    id = 1
    all_log_txt = []
    folder_location = f'data/resto-list/date_{date}'
    driver = webdriver.Chrome()
    restaurants = []
    detailed_restaurants = []
    rating_restaurants = []
    comments = []
    start_time = time.time()

    def create_log(self, status: str, value: str):

        # Register time
        date = datetime.date.today().strftime('%d-%m-%Y')
        hour = datetime.datetime.now().strftime('%H:%M:%S')
        # Create readable log
        log_info = f"[{date} {hour}] {status}: {value}"
        print(log_info)
        # Prepare text to save in file
        self.all_log_txt.append(log_info)

        # Create a log file if exists and update log
        if not os.path.exists(f'{self.folder_location}/logs/'):
            os.makedirs(f'{self.folder_location}/logs/')

        with open(f"{self.folder_location}/logs/bot_operation_{self.date}_{self.hour}.log", "w") as log_file:
            log_file.write("\n".join(gathering.all_log_txt))

    def initialize_gathering(self, page_link: str, *args):

        try:
            # Display info on terminal and write in log
            with open('version.json', 'r') as f:
                version_info = json.load(f)
                major = version_info["major"]
                minor = version_info["minor"]
                patch = version_info["patch"]
                release = version_info["release"]
                description = version_info["description"]

                self.create_log('INFO', f'Version: {major}.{minor}.{patch}-{release}')
                self.create_log('INFO', f'Version: {description}')

            self.create_log('INFO', 'Page is loading...')
            # Initializing web driver
            self.driver.get(page_link)
            time.sleep(3)

            # Initiate soup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # Track number of results
            num_result_block = soup.find("a", id="tab-restaurants-active")
            num_restults = num_result_block.find("span").text.replace("(", "").replace(")","")

            # Track number of pages
            num_pages = soup.find("div", class_="mb0 mt40 color-dark bold fs-16 text-center p10").text.split()[-1].strip()
            # Saving infon into log
            self.create_log('INFO', 'Started')
            self.create_log('INFO' , f'Number of result(s) for scraping {num_restults}')
            self.create_log('INFO', f'Number of page(s) for scraping {num_pages}')

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
            self.create_log('ERROR', full_trace)
            self.create_log('WARNING', 'Scraping process interupted no record was made.')


    def get_data(self, min_page: int, max_page: int, pages = None):

        # Scrape by page
            def execute_scrape(page_num):

                # Start scraping content to the instruction page
                web_link = self.data_source + f"&page={page_num}#{page_num}"
                self.driver.get(web_link)
                time.sleep(3)

                #Using beautiful soup to get the list of restaurants
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                resto_block = soup.find_all("div", class_='search-result')

                self.create_log('INFO', f'Starting to fetch on page {page_num}')

                # Scrape all content block

                for resto in resto_block:
                    try:
                        # From main Div
                        lat = resto.get('data-lat')
                        lon = resto.get('data-lon')

                        # From link
                        link = resto.find_all('a')
                        resto_link = link[2]
                        unique_page = resto_link.get('href')
                        raw_name = resto_link.text.split()
                        name = " ".join(raw_name)

                        # From hash tag
                        hash_div = resto.find('div', class_='color-gray mb5 lh-normal search-cuisine-box')
                        # Skip if there is no hash tag
                        if hash_div != None:
                            hash_elements = hash_div.find_all('a')

                            hash_tags = []
                            for hash in hash_elements:
                                hash_tags.append(hash.text.strip())
                    #################### RECORD ####################
                        self.restaurants.append(
                            {
                                "id": self.id,
                                "name": name,
                                "latitude": lat,
                                "longitude": lon,
                                "hash_tags": ",".join(hash_tags),
                                "unique_page": unique_page
                            }
                        )

                        # Get details of in unique page for restaurant
                        self.get_detailed_page(unique_page, self.id)
                        self.create_log('INFO', f'{len(self.restaurants)} - data')

                        self.id += 1
                        # Stop if reached the last page
                        if page_num == max_page+ 1:
                            self.create_log('INFO', "Bot's task completed")
                            break

                    except Exception:
                        full_trace = traceback.format_exc()
                        self.create_log('ERROR', full_trace)
                        self.create_log('WARNING', f'Encountered at page {page_num} after {len(self.restaurants)} element(s) recorded')
                        self.create_log('INFO', f"Got issue with id: {self.id}")
                        self.id += 1
                        continue

                # Update data every iteration
                self.record_data()


            # Execute a range or list of page
            if max_page != 0:

                for page_num in range(min_page, max_page):
                    execute_scrape(page_num)

            elif pages is not None:
                for page in pages:
                    execute_scrape(page)

            self.record_data()

    def get_detailed_page(self, link, id_key):

        def try_element_exist(soup, element, class_name, numeric):

            info = soup.find(element, class_=class_name)

            if info is None and numeric:
                return 0
            else:
                return info

        def extract_soup(elements):
            this_list = []
            for element in elements:
                this_list.append(element.text.strip())
            return this_list

        self.driver.get(link)
        time.sleep(3)
        # Get page soup
        detailed_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        #################### DETAILS ####################
        average_price = detailed_soup.find('div', class_='restaurant-price').get('data-tooltip')
        address = detailed_soup.find('span', class_='street-address').text.strip()
        description = detailed_soup.find('div', class_='aboutus-text').text.strip()

        amount_of_picture  = try_element_exist(detailed_soup, 'a','btn-e-see-photos', True)
        # Filter out the number of picture
        if amount_of_picture is not None:
            amount_of_picture = re.findall('\d', amount_of_picture.text)

        # Get features list
        features_group = try_element_exist(detailed_soup, 'div', "row mt5 mb5", False)
        features = []
        if features_group is not None:
            features_group.find_all('span', class_='action-btn-group')
            features = extract_soup(features)

        #################### RATINGS ####################
        average_rating = try_element_exist(detailed_soup, 'span', 'google_rating_bold', True)
        if average_rating is not None: average_rating = average_rating.text.strip()
        else: average_rating = None

        amount_of_rating = detailed_soup.find('a', class_='reviewscard_rating').text.strip()
        # Filter out the number of rating
        amount_of_rating = re.findall('\d', amount_of_rating)
        #################### COMMENTS ###################

        # Check for at least one comment exist
        customer_rating_test = try_element_exist(detailed_soup, 'span', 'icon-box wider ratings border-good icon-dark icon-circle text-thick', False)

        customer_rating = []
        customer_comment = []
        customer_rating_date = []
        if customer_rating_test is not None:
            customer_ratings = detailed_soup.find_all('div', class_='pull-right')
            for rating in customer_ratings[:-1]:
                if rating.find('span') is not None:
                    customer_rating.append(rating.find('span').text.strip())


            customer_comments = detailed_soup.find_all('p', class_='mt20 mb20 reviews-desc')
            customer_rating_dates = detailed_soup.find_all('span', class_='review-date')

            customer_comment = extract_soup(customer_comments)
            customer_rating_date = extract_soup(customer_rating_dates)


        #################### RECORD ####################
        self.detailed_restaurants.append(
            {
                "id_resto": id_key,
                "amount_pictures": "".join(amount_of_picture),
                "address": address,
                "average_price": average_price,
                "features": ",".join(features),
                "description" : description
            }
        )

        self.rating_restaurants.append(
            {
                "id_resto": id_key,
                "average_rating": average_rating,
                'amount_of_rating': ''.join(amount_of_rating)
            }
        )

        for i in range(len(customer_rating)):
            self.comments.append(
                {
                    "id_resto": id_key,
                    "customer_rating": customer_rating[i],
                    "customer_comment": customer_comment[i],
                    "customer_rating_date": customer_rating_date[i]
                }
            )

    def record_data(self):

        # Create folder by date or use existing folder
        if not os.path.exists(self.folder_location):
            os.makedirs(self.folder_location)

        data_location = {
            "restaurants.csv": self.restaurants,
            "restaurant_details.csv": self.detailed_restaurants,
            "restaurant_comments.csv": self.comments
        }

        # Iterate through data and save into csv
        for file_name, data in data_location.items():
            df = pd.DataFrame(data)
            df.to_csv(f'{self.folder_location}/{file_name}', index=False)

#Initialize
gathering = GatherData()

# Scrape the page
gathering.initialize_gathering(gathering.data_source, 'all')
