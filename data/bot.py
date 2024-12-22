# Basic Imports
import pandas
import csv
import time
import datetime
import traceback

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
    start_time = time.time()

    def create_log(self, status: str, value: str):

        # Create readable log
        log_info = f"[{self.date} {self.hour}] {status}: {value}"
        print(log_info)
        # Prepare text to save in file
        self.all_log_txt.append(log_info)

    def initialize_gathering(self, page_link: str, *args):

        try:
            # Display progression on terminal and write in log
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
                        self.get_data(1, int(num_pages))


                if isinstance(item, (list, tuple)):
                    if len(item) == 1:
                        self.get_data(1, item[0])
                    elif len(item) == 2:
                        self.get_data(item[0], item[1])
                    else:
                        self.get_data(0, 0, item)
        except Exception:
            full_trace = traceback.format_exc()
            self.create_log('ERROR', full_trace)
            self.create_log('WARNING', 'Scraping process interupted no record was made.')


    def get_data(self, min_page: int, max_page: int, pages = None):


        # Scrape by page
        try:
            for page_num in range(min_page, max_page + 1):

                # Start scraping content to the instruction page
                web_link = self.data_source + f"&page={page_num}#{page_num}"
                self.driver.get(web_link)
                time.sleep(3)

                #Using beautiful soup to get the list of restaurants
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                resto_block = soup.find_all("div", class_='search-result')

                self.create_log('INFO', 'Starting to fetch...')
                restaurants = []

                # Scrape all content block
                for i, resto in enumerate(resto_block, start=1):

                    # From main Div
                    lat = resto.get('data-lat')
                    lon = resto.get('data-lon')

                    # From link
                    link = resto.find_all('a')
                    resto_link = link[2]
                    unique_page = resto_link.get('href')
                    name = resto_link.text.strip()

                    # From span
                    address = resto.find('span', id=f'{i - 1}-searchaddress').text.strip()

                    # From hash tag
                    hash_div = resto.find('div', class_='color-gray mb5 lh-normal search-cuisine-box')
                    hash_elements = hash_div.find_all('a')

                    hash_tags = []
                    for hash in hash_elements:
                        hash_tags.append(hash.text.strip())

                    restaurants.append(
                        {
                            "id": i,
                            "name": name,
                            "latitude": lat,
                            "longitude": lon,
                            "address": address,
                            "hash_tags": ",".join(hash_tags),
                            "unique_page": unique_page
                        }
                    )

                print(f'Page {page_num} is done')
                print(len(restaurants))

                #TODO remove line below after test
                break
                # Stop if reached the last page
                if page_num == max_page:
                    break
        except Exception:
            full_trace = traceback.format_exc()
            self.create_log('ERROR', full_trace)
            self.create_log('WARNING', f'Process were interrupted at page {page_num} after {i - 1} element(s) recored')

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
gathering.initialize_gathering(gathering.data_source, "all")

# Create a log file
with open(f"logs/bot_log_{gathering.date}_{gathering.hour}.log", "a") as log_file:
    log_file.write("\n".join(gathering.all_log_txt))
