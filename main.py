
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
    def try_val(prompt, 
                allow_range_check, 
                allow_min_check, 
                min_val = None, 
                max_val = None):
       
        while True:
            
            try:
                choice = int(input(prompt + "\n-->"))

                if allow_range_check:
                    if choice < min_val or choice > max_val:
                        print(f"Please choose between {min_val} and {max_val}...\n")
                        continue

                if allow_min_check:
                    if choice < min_val:
                        print(f"Please choose an integer of {min_val} or greater")
                        continue

            except ValueError:
                print("Please enter an integer...\n")
                continue

            return choice


    method_scrape = try_val("Choose method of webscraping ? \n(1) All\n(2) Number of pages\n(3) Range of pages\n(4) Specific page", True, False, 1, 4)
    
    match method_scrape:
        case 1:
            return "all"
        case 2:
            return [1, try_val("Number of pages?", False, True, 1)]
        case 3:
            start_page= try_val("Starting page number?",False, True, 1)
            end_page= try_val("Ending page number?",False, True, start_page)
            return [start_page, end_page]
        case 4:
            return try_val("Which page to get?")
            

        
    

processor.initialize_gathering(method())
