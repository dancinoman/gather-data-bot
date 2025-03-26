import os
import datetime

class Logger:
    """
    Responsible for creating logs for the bot that describes operations, status, or amount of data.
    The logs are saved in an organized folder along with data collected to get easy tracking performance.
    """
    date = datetime.date.today().strftime('%d-%m-%Y')
    hour = datetime.datetime.now().strftime('%H:%M:%S')
    full_log_txt = []

    def __init__(self, folder_location: str):
        self.folder_location = folder_location

    def create_log(self, status: str, value: str):
        # Register time

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
