import os
import datetime
import pandas as pd

class RecordData:
    """"
    Main purpose is to save data collected to a loclal folder.
    """
    date = datetime.date.today().strftime('%d-%m-%Y')
    hour = datetime.datetime.now().strftime('%H:%M:%S')
    full_log_txt = []
    restaurants = []
    detailed_restaurants = []
    rating_restaurants = []
    comments = []

    def __init__(self, folder_location: str):
        self.folder_location = folder_location

    def create_log(self, status: str, value: str):
        """
        Responsible for creating logs for the bot that describes operations, status, or amount of data.
        The logs are saved in an organized folder along with data collected to get easy tracking performance.
        """
        # Create readable log
        log_info = f"[{self.date} {self.hour}] {status}: {value}"
        print(log_info)
        # Prepare text to save in file
        self.full_log_txt.append(log_info)

        # Create a log file if exists and update log
        if not os.path.exists(f'{self.folder_location}/logs/'):
            os.makedirs(f'{self.folder_location}/logs/')

        with open(f"{self.folder_location}/logs/bot_operation_{self.date}_{self.hour}.log", "w") as log_file:
            log_file.write("\n".join(self.full_log_txt))

    def save_csv(self):
        """
        Collect all data and convert to csv files.
        """
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
