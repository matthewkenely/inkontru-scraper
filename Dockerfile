# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

ENV HOST 0.0.0.0

# Install necessary packages (curl, wget, unzip, gnupg)
RUN apt-get update && apt-get install -y curl wget unzip gnupg

RUN apt-get update \
    && apt-get install -y \
        libnss3 \
        libcups2 \
        libgconf-2-4 \
        libxss1 \
        libappindicator1 \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libpango-1.0-0 \
        libx11-xcb1 \
        libxtst6 \
        xdg-utils \
        lsb-release \
        wget \
        unzip \
        gnupg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Download and install ChromeDriver
RUN mkdir -p /usr/local/bin \
    && wget -v -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip \
    && unzip -o /tmp/chromedriver.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/chromedriver-linux64/chromedriver \
    && rm /tmp/chromedriver.zip


# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Define the command to run your script using CMD which runs on the terminal
CMD ["python", "./main.py"]
