
# Basic imports
import datetime
import os

from dotenv import load_dotenv
load_dotenv()

# import classes
from app.processor import Processor

#Initialize
date = datetime.date.today().strftime('%d-%m-%Y')
folder_location = f'data/resto-list/date_{date}'
website_address = os.environ.get('WEBSITE_ADDRESS')
processor = Processor(website_address, folder_location)

# Initiate the method of webscraping with the user input
def method():
    """
    Take the input to choose a method
    
    Returns: string input from the user web scraping choice
    """
    while True:
        
        try:
            method_scrape = int( input("Choose method of webscraping ? \n(1) All\n(2) Number of pages\n(3) Range of pages\n(4) Specific page\n-->"))

        except ValueError:
            print("Please enter an integer...\n")

        if method_scrape < 1 or method_scrape > 4:
            print("Please choose between 1 and 4...")
        else:
        
        
    
method()
#processor.initialize_gathering(method())
