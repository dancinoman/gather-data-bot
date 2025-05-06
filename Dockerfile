# Use official Python image
FROM python:3.11-slim

# Create app directory and set ownership
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser /app

# Set Chrome dependencies
RUN apt-get update && apt-get install -y wget gnupg ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils

# Install Chrome
RUN wget --no-check-certificate https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    dpkg -i google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and assign ownership
COPY . .
RUN chown -R appuser /app

# Switch to non-root user
USER appuser

EXPOSE 5000
CMD ["python", "main.py"]
