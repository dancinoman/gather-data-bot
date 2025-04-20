# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies for Chrome
RUN apt-get update && apt-get install -y wget gnupg ca-certificates

# Download and install Google Chrome
RUN wget --no-check-certificate https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && dpkg -i google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port that Flask will run on (default is 5000)
EXPOSE 5000

# Define the command to run your Flask application
CMD ["python", "main.py"]
