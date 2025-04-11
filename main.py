# Basic Imports
import os
import sys
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

class GatherData:


    hour = datetime.datetime.now().strftime('%H:%M:%S')
    id = 1
    all_log_txt = []

    driver = webdriver.Chrome()
    start_time = time.time()

    def __init__(self, website_address: str):
        self.website_address = website_address

    def initialize_gathering(self, *args):

        try:
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
                    record.restaurants.append(
                        {
                            "id": self.id,
                            "name": name,
                            "latitude": lat,
                            "longitude": lon,
                            "hash_tags": ",".join(hash_tags),
                            "unique_page": unique_page
                        }
                    )

                    record.create_log('INFO', f'#{len(record.restaurants)} - {record.restaurants[-1]["name"]} recorded')

                    # Save file to csv from individual page
                    self.driver.get(unique_page)
                    time.sleep(3)
                    record.save_csv(scrape_frame.individual_content(self.driver.page_source, self.id))

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

        self.record_data()

    def get_detailed_page(self, link, id_key):

        """def extract_soup(elements):
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

        amount_of_picture  = detailed_soup.find('a','btn-e thick bold black rounded mb10 mt30 block')

        # Filter empty value
        if amount_of_picture is not None:
            amount_of_picture = re.findall('\d', amount_of_picture.text)
        else:
            amount_of_picture = ["0"]

        # Get features list
        features_group = detailed_soup.find('div', "row mt5 mb5", False)
        features = []

        if features_group is not None:
            features_group.find_all('span', class_='action-btn-group')
            features = extract_soup(features)

        #################### RATINGS ####################
        average_rating = detailed_soup.find('span', 'google_rating_bold')
        if average_rating is not None: average_rating = average_rating.text.strip()
        else: average_rating = None

        amount_of_rating = detailed_soup.find('a', class_='reviewscard_rating')

        if amount_of_rating is not None:
            amount_of_rating = amount_of_rating.text.strip()
            amount_of_rating = re.findall('\d', amount_of_rating)
            amount_of_rating = ''.join(amount_of_rating)
        else:
            amount_of_rating = None
        #################### COMMENTS ###################

        # Check for at least one comment exist
        customer_rating_test = detailed_soup.find('span', 'icon-box wider ratings border-good icon-dark icon-circle text-thick')
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
        record.detailed_restaurants.append(
            {
                "id_resto": id_key,
                "amount_pictures": "".join(amount_of_picture),
                "address": address,
                "average_price": average_price,
                "features": ",".join(features),
                "description" : description
            }
        )

        record.rating_restaurants.append(
            {
                "id_resto": id_key,
                "average_rating": average_rating,
                'amount_of_rating': amount_of_rating
            }
        )

        for i in range(len(customer_rating)):
            record.comments.append(
                {
                    "id_resto": id_key,
                    "customer_rating": customer_rating[i],
                    "customer_comment": customer_comment[i],
                    "customer_rating_date": customer_rating_date[i]
                }
            """


#Initialize
date = datetime.date.today().strftime('%d-%m-%Y')
folder_location = f'data/resto-list/date_{date}'
website_address = os.environ.get('WEBSITE_ADDRESS')
gathering = GatherData(website_address)
record = RecordData(folder_location)
scrape_frame = Scrape()

# Scrape the page
gathering.initialize_gathering("all")
