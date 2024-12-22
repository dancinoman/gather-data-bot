# Basic Imports
import pandas
import csv
import time
import datetime

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

class GatherData:

    data_source = "https://www.restomontreal.ca/s/?restaurants=greater-montreal&lang=en"
    start_time = time.time()

    def display_progress(self, message: str):

        time_seconds = round(time.time() - self.start_time)
        time_format = str(datetime.timedelta(seconds=time_seconds))
        print(f"({time_format}) {message}")

    def create_log(self, name: str, value: str):
        print("log: ", name, value)

    def initialize_gathering(self, page_link: str, page_range: list):

        # Display progression on terminal
        self.display_progress('Page is loading...')
        # Initializing webdriver
        driver = webdriver.Chrome()
        driver.get(page_link)
        time.sleep(3)

        #Using beautiful soup to get the list of restaurants
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        resto_block = soup.find_all("div", class_='search-result')

        #Track number of results
        num_result_block = soup.find("a", id="tab-restaurants-active")
        num_restults = num_result_block.find("span").text.replace("(", "").replace(")","")

        self.display_progress(f'Today {num_restults} are available')
        # Saving infon into log
        self.create_log('Scraping date: ', datetime.date.today().strftime('%d %B, %Y'))
        self.create_log('Scraping time: ', datetime.datetime.now().strftime('%H:%M:%S'))
        self.create_log('Number of results: ', num_restults)
        self.display_progress('Info located ready to fetch...')

        restaurants = []

        for i, resto in enumerate(resto_block):

            # From main Div
            lat = resto.get('data-lat')
            lon = resto.get('data-lon')

            # From link
            link = resto.find_all('a')
            resto_link = link[2]
            perso_page = resto_link.get('href')
            name = resto_link.text.strip()

            # From span
            address = resto.find('span', id=f'{i}-searchaddress').text.strip()

            # From hash tag
            hash_div = resto.find('div', class_='color-gray mb5 lh-normal search-cuisine-box')
            hash_elements = hash_div.find_all('a')

            hash_tags = []
            for hash in hash_elements:
                hash_tags.append(hash.text.strip())
            if i == 2:
                break

        def run_next_page(self):
            pass
            #all elements example
            #name = game.find('a', class_='b').text.strip()

            # Get another list inside of the element of list
            #elements = game.find_all('td', class_ = 'dt-type-numeric')

            #price = elements[2].text.replace('CDN$', '').strip()
            #rating = elements[3].text.replace('%', '').strip()
            #release_date = elements[4].text.strip()
            #followers = elements[5].text.replace(',', '').strip()
            #peak_online = elements[7].text.replace(',', '').strip()

            #games.append({
            #    'name'         : name,
            #    'price'        : price,
            #    'rating'       : rating,
            #    'release date' : release_date,
            #    'followers'    : followers,
            #    'max peak'     : peak_online
            #})

        print(sorted(hash_tags))
        #Then change page
        #resto_list = soup.find_all('tr', class_='app')
        # Interact with webpage
        #wait = WebDriverWait(driver, 15).until(lambda x : x.find_element(By.ID, 'dt-length-0'))
        #get_input = Select(driver.find_element(By.ID, 'dt-length-0'))
        #get_input.select_by_visible_text('All (slow)')
        #wait = WebDriverWait(driver, 5)
        #wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='main']")))

        #for  in games_list:


        #print(f' Writing {len(games)} element(s)')
        #with open(f'data/csv/games_top_{year}.csv', 'w') as file:
        #    writer = csv.DictWriter(file, fieldnames= games[0].keys())
        #    writer.writeheader()
        #    writer.writerows(games)
        #print('1 page done successfully')
        #driver.quit()

#Initialize
gathering = GatherData()

# Scrape the page
gathering.initialize_gathering(gathering.data_source, [1])
