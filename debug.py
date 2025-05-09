import os
from dotenv import load_dotenv
load_dotenv()

website_address = os.environ.get('WEBSITE_ADDRESS')

print(website_address)