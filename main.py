
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

# Initiate the method of gathering the data
processor.initialize_gathering("all")
