
# Basic imports
from bs4 import BeautifulSoup
import time
import re
import traceback

# Selenium imports
from selenium import webdriver

# Import classes from folder
from app.record_data import RecordData

class Scrape:

    def __init__(self, website_address: str, folder_location: str):
        self.id = 1
        self.website_address = website_address
        self.folder_location = folder_location
        self.driver = webdriver.Chrome()
        self.restaurants = []
        self.detailed_restaurants = []
        self.comments = []

    def get_page(self, min_page: int, max_page: int, pages = None):
        """
        Get the data page by page.

        Args:
            min_page(int): The minimum page number to start scraping from.
            max_page(int): The maximum page number to stop scraping at.
            pages(int, None): A list of specific page numbers to scrape.
        """
        # Calling classes
        record = RecordData(self.folder_location)

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
                    unique_page = self.cover_content(resto, self.id)

                    # Go to unique page details to get more info
                    self.driver.get(unique_page)
                    time.sleep(3)
                    all_info = self.individual_content(self.driver.page_source, self.id)

                    # Store to CSV
                    record.save_csv(*all_info)
                    record.create_log('INFO', f'#{len(self.restaurants)} - {self.restaurants[-1]["name"]} recorded')

                    #Prepare for next loop
                    self.id += 1
                    # Stop if reached the last page
                    if page_num == max_page+ 1:
                        record.create_log('INFO', "Bot's task completed")
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

    def cover_content(self, resto: BeautifulSoup, id: int):
        """
        Get the content on search page.

        Args:
            resto(BeautifulSoup.find(<content>)): The restaurant block to scrape.
            id(int): The unique ID of the restaurant.
        """
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
        self.restaurants.append(
            {
                "id": id,
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "hash_tags": ",".join(hash_tags),
                "unique_page": unique_page
            }
        )

        return unique_page

    def individual_content(self, page_source: webdriver, id: int):
        """
        Scrapes individual restaurant pages.

        Args:
            page_source(webdriver): The page source of the restaurant.
            id(int): The unique ID of the restaurant.
        """

        # Get page soup
        detailed_soup = BeautifulSoup(page_source, 'html.parser')

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


        if features_group is not None:
            features_group.find_all('span', class_='action-btn-group')
            features = [element.text.strip() for element in features_group if element]
        else:
            features = []

        #################### RATINGS ####################
        average_rating = detailed_soup.find('span', 'google_rating_bold')
        if average_rating is not None: average_rating = average_rating.text.strip()
        else: average_rating = None

        amount_of_rating = detailed_soup.find('a', class_='reviewscard_rating')

        if amount_of_rating is not None:
            amount_of_rating = amount_of_rating.text.strip()
            amount_of_rating = re.findall('\d', amount_of_rating)
            amount_of_rating = ''.join(amount_of_rating)

        #################### COMMENTS ###################

        # Check for at least one comment exist
        customer_rating = detailed_soup.findAll('div', 'reviews-card mb20')

        self.detailed_restaurants.append(
            {
                "id": id,
                "amount_pictures": "".join(amount_of_picture),
                "address": address,
                "average_price": average_price,
                "features": ",".join(features),
                "description" : description
            }
        )

        for cus_rating in customer_rating:
            self.comments.append({
                "id": id,
                "rating": cus_rating.find("div", "pull-right").find("span").text.strip(),

                "text": cus_rating.find("p", "mt20 mb20 reviews-desc").text.strip(),
                "date": cus_rating.find("span", "review-date").text.strip(),
                "average_rating": average_rating,
                'amount_of_rating': amount_of_rating
            })

        return self.restaurants, self.detailed_restaurants, self.comments
