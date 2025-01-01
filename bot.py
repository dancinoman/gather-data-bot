# Basic Imports
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

from bs4 import BeautifulSoup
import bs4

class GatherData:

    driver = webdriver.Chrome()
    data_source = "https://www.restomontreal.ca/s/?restaurants=greater-montreal&lang=en"
    date = datetime.date.today().strftime('%d-%m-%Y')
    hour = datetime.datetime.now().strftime('%H:%M:%S')
    all_log_txt = []
    restaurants = []
    detailed_restaurants = []
    rating_restaurants = []
    start_time = time.time()

    def create_log(self, status: str, value: str):

        # Create readable log
        log_info = f"[{self.date} {self.hour}] {status}: {value}"
        print(log_info)
        # Prepare text to save in file
        self.all_log_txt.append(log_info)

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
            # Initializing webdriver
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
                        self.get_data(1, int(num_pages + 1))


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


            def execute_scrape(page_num, id):

                try:
                    # Start scraping content to the instruction page
                    web_link = self.data_source + f"&page={page_num}#{page_num}"
                    self.driver.get(web_link)
                    time.sleep(3)

                    #Using beautiful soup to get the list of restaurants
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    resto_block = soup.find_all("div", class_='search-result')

                    self.create_log('INFO', f'Starting to fetch on page {page_num}')

                    # Scrape all content block
                    for i, resto in enumerate(resto_block):

                        # From main Div
                        lat = resto.get('data-lat')
                        lon = resto.get('data-lon')

                        # From link
                        link = resto.find_all('a')
                        resto_link = link[2]
                        unique_page = resto_link.get('href')
                        raw_name = resto_link.text.split()
                        name = " ".join(raw_name)

                        # From span
                        address = resto.find('span', id=f'{i}-searchaddress').text.strip()

                        # From hash tag
                        hash_div = resto.find('div', class_='color-gray mb5 lh-normal search-cuisine-box')
                        # Skip if there is no hash tag
                        if hash_div != None:
                            hash_elements = hash_div.find_all('a')

                            hash_tags = []
                            for hash in hash_elements:
                                hash_tags.append(hash.text.strip())

                        self.restaurants.append(
                            {
                                "id": id,
                                "name": name,
                                "latitude": lat,
                                "longitude": lon,
                                "address": address,
                                "hash_tags": ",".join(hash_tags),
                                "unique_page": unique_page
                            }
                        )

                        # Get details of in unique page for restaurant
                        self.get_detailed_page(unique_page, id)

                        id += 1

                        self.create_log('INFO', f'{len(self.restaurants)} - data')


                        # Stop if reached the last page
                        if page_num == max_page+ 1:
                            self.create_log('INFO', "Bot's task completed")
                            break
                except Exception:
                    full_trace = traceback.format_exc()
                    self.create_log('ERROR', full_trace)
                    self.create_log('WARNING', f'Encountered at page {page_num} after {i} element(s) recorded')

            # Execute a range or list of page
            id = 1

            if max_page != 0:

                for page_num in range(min_page, max_page):
                    execute_scrape(page_num, id)

            elif pages is not None:
                for page in pages:
                    execute_scrape(page, id)

            # Save into csv file
                df = pd.DataFrame

                df = pd.DataFrame(self.restaurants)
                df.to_csv('data/resto-list/restaurants.csv', index=False)
                df = pd.DataFrame(self.detailed_restaurants)
                df.to_csv('data/resto-list/restaurant_details.csv', index=False)
                df = pd.DataFrame(self.rating_restaurants)
                df.to_csv('data/resto-list/restaurant_ratings.csv', index=False)


    def get_detailed_page(self, link, id_key):

        self.driver.get(link)
        time.sleep(3)
        # Get page soup
        detailed_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        amount_of_picture  = detailed_soup.find('a', class_='btn-e-see-photos').text.strip()
        average_price = detailed_soup.find('div', class_='restaurant-price').get('data-tooltip')
        description = detailed_soup.find('div', class_='aboutus-text').text.strip()
        affiliated = detailed_soup.find('h3', class_='title-section').text.strip()
        # Get features list
        features_group = detailed_soup.find('div', class_="row mt5 mb5").find_all('span', class_='action-btn-group')
        features = []

        for feature in features_group:
            features.append(feature.find('span').text.strip())



        average_rating = detailed_soup.find('span', class_='google_rating_bold').text.strip()
        amount_of_rating = detailed_soup.find('a', class_='reviewscard_rating').text.strip()
        amount_of_rating = re.findall('\d', amount_of_rating)

        self.detailed_restaurants.append(
            {
                "id_resto": id_key,
                "amount_pictures": amount_of_picture,
                "average_price": average_price,
                "features": ",".join(features),
                "affiliated": affiliated,
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



#Initialize
gathering = GatherData()

# Scrape the page
gathering.initialize_gathering(gathering.data_source, [1,3])

# Create a log file
with open(f"logs/bot_log_{gathering.date}_{gathering.hour}.log", "a") as log_file:
    log_file.write("\n".join(gathering.all_log_txt))
