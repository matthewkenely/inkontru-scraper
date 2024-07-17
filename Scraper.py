import sys
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import pandas as pd
from Event import Inkontru_Event

from time import sleep
# import logging
# logging.basicConfig(level=logging.DEBUG)

from concurrent.futures import ThreadPoolExecutor
import threading

LINK_WAIT = 10
ELEMENT_WAIT = 1


class Scraper:
    
    def __init__(self, sources_page_links, sources_events_links):
        
        self.sources_page_links = sources_page_links
        self.sources_events_links = sources_events_links
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
        )

        # chrome_options.add_argument("--disable-javascript")


        prefs = {
            "profile.default_content_setting_values": {
                "fonts": 2,  # Block fonts
                "images": 2,  # Block images (optional, can be adjusted as needed)
                # "javascript": 2  # Block JavaScript (optional, can be adjusted as needed)
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)


        self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver.set_page_load_timeout(60)
        # Set element timeout to 2 seconds
        self.driver.implicitly_wait(2)
    
        self.sources_events_page = {
            "dates" : [],
            "location" : "",
            "time" : "",
            "interval" : "",
            "duration" : "",
            "audience-level" : "",
            "fee" : ""
        }

        self.scrape_events_xpaths = {
            "festivals_malta" : {
                "title" : "//*[contains(@class, 'comp-kwko1lma')]/h3/span/span/span",
                "date" : "//*[contains(@id, 'comp-kwkovp46')]/h6/span",
                "other_dates" : "",
                "time" : "//*[contains(@id, 'comp-kwkoy64x')]/h6/span",
                "location" : "//*[contains(@id, 'omp-kwkoxvjk')]/h6/span",
                "duration" : "//*[contains(@id, 'comp-kwkoynk3')]/h6/span",
                "audience_level" : "//*[contains(@id, 'comp-kzzd8mur')]/h6/span",
                "fee" : "//*[contains(@id, 'comp-kwkoyqiq')]/h6/span"
            },
            "teatru_malta" : {
                "title" : "//*[contains(@class, 'title-cont')]/h1",
                "date" : "//span[contains(text(), 'Date')]/../following-sibling::div[1]/span",
                "other_dates" : "",
                "time" : "//span[contains(text(), 'Time')]/../following-sibling::div[1]/span",
                "location" : "//span[contains(text(), 'Location')]/../following-sibling::div[1]/span",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "teatru_manoel" : {
                "title" : "//*[contains(@class, 'hew-title')]/a", #/text()
                "date" : "//*[contains(@class, 'hew-date')]", #/text()
                "other_dates" : "",
                "time" : "//*[contains(@class, 'se-eventformat-time')]",
                "location" : "",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "zfin_malta" : {
                "title" : "//h1[contains(@class, 'tribe-events-single-event-title')]", 
                "date" : "//span[@class='tribe-event-date-start']", 
                "other_dates" : "", 
                "time" : "//span[@class='tribe-event-date-start']",
                "location" : "//*[@class='tribe-venue']",
                "duration" : "",
                "audience_level" : "",
                "fee" : "//*[contains(text(), '€')]//parent::strong"
            },
            "kreattivita" : {
                "title": "//h1[contains(@class, 'tribe-events-single-event-title')]",
                "date": "//span[contains(@class, 'tribe-event-date-start')]",
                "other_dates": "",
                "time": "//span[contains(@class, 'tribe-event-date-start') or contains(@class, 'tribe-event-time')]",
                "location": "//span[contains(@class, 'tribe-street-address')]",
                "duration": "//div[@class='additional']//div[contains(@class, 'col-md-6') and text()='Duration']/following-sibling::div[contains(@class, 'col-md-6')]",
                "audience_level": "//div[@class='additional']//div[contains(@class, 'col-md-6') and text()='Cert']/following-sibling::div[contains(@class, 'col-md-6')]",
                "fee": "//div[@class='ticket']//div[contains(@class, 'col-md-6') and text()='Adult']/following-sibling::div[contains(@class, 'col-md-6')]"
            },
            "micas" : {
                # Placeholder, this is replaced with the web page title
                "title" : "//strong[contains(text(), 'Date')]/parent::p | //strong[contains(text(), 'DATE')]/parent::p",
                "date" : "//strong[contains(text(), 'Date')]/parent::p | //strong[contains(text(), 'DATE')]/parent::p",
                "other_dates" : "",
                "time" : "//strong[contains(text(), 'Time')]/parent::p | //strong[contains(text(), 'TIME')]/parent::p",
                "location" : "//strong[contains(text(), 'Venue')]/parent::p | //strong[contains(text(), 'VENUE')]/parent::p",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "tnd" : {
                "title" : "//h1[contains(@data-hook, 'event-title')]",
                "date" : "//*[contains(@data-hook, 'event-short-date')]",
                "other_dates" : "",
                "time" : "//*[@data-hook='event-full-date']",
                "location" : "//*[@data-hook='event-short-location']",
                "duration" : "",
                "audience_level" : "",
                "fee" : "//*[@data-hook='price']"
            },
            "malta_orchestra" : {
                "title" : "//div[contains(@class, 'em-event')]/h1",
                "date" : "//section[@class='container']//div[contains(., 'DATE:')]/strong[1]",
                "other_dates" : "",
                "time" : "//section[@class='container']//div[contains(., 'TIME:')]/strong[2]",
                "location" : "//strong[contains(text(), 'Location')] | //strong[contains(text(), 'LOCATION')] | //a[contains(@href, '/locations/')]",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "ziguzajg" : {
                "title" : "//h2[contains(@class, 'elementor-heading-title')]",
                "date" : "//div[@class='elementor-widget-container']//p[not(ancestor::del)]//strong | //div[@class='elementor-widget-container']//p[not(ancestor::del)]//b",
                "other_dates" : "",
                "time" : "//div[@class='elementor-widget-container']//p[not(ancestor::del)]//strong | //div[@class='elementor-widget-container']//p[not(ancestor::del)]//b",
                "location" : "(//h3)[4]//span",
                "duration" : "(//h3)[2]//span",
                "audience_level" : "//h2[contains(text(), 'Age')]",
                "fee" : "(//h3)[5]//span"
            },
            "heart_of_gozo" : {
                "title" : "//h1[contains(@class, 'event__heading-1')]",
                "date" : "//p[contains(@class, 'event__date-time')]",
                "other_dates" : "",
                "time" : "//p[contains(@class, 'event__byline')]",
                "location" : "//p[contains(@class, 'event__byline')]",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "teatru_aurora" : {
                "title" : "//h1[contains(@class, 'mkdf-st-title')]",
                "date" : "//h6[contains(@class, 'mkdf-custom-font-holder')]",
                "other_dates" : "",
                "time" : "",
                "location" : "",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
            "shows_happening" : {
                "title" : "//h1[contains(@class, 'event-name')]",
                "date" : "//p[contains(@class, 'event-date-time-details')] | //p[contains(@class, 'event-date-time-details')]//span",
                "other_dates" : "",
                "time" : "",
                "location" : "//p[contains(@class, 'event-location-details')]//span",
                "duration" : "",
                "audience_level" : "//div[contains(@class, 'requirement-info')]//p[contains(@class, 'data')]",
                "fee" : "//div[contains(@class, 'ticket-price')]//p"
            },
            "ticketline" : {
                "title" : "(//h3)[2]",
                # Get parent of //span[contains(text(), 'Date:')]
                "date" : "//span[contains(text(), 'Date:')]/parent::span",
                "other_dates" : "",
                "time" : "//span[contains(text(), 'Time:')]/parent::span",
                "location" : "//span[contains(text(), 'Venue')]/parent::div//span[2]",
                "duration" : "",
                "audience_level" : "",
                "fee" : ""
            },
        }


    def get_source_from_url(self, url):
        if "www.festivals.mt/" in url:
            return "festivals_malta"
        if "teatrumanoel.mt/" in url:
            return "teatru_manoel"
        if "teatrumalta.org.mt/" in url:
            return "teatru_malta"
        if "www.zfinmalta.org/" in url:
            return "zfin_malta"
        if "kreattivita.org" in url:
            return "kreattivita"
        if "micas.art/" in url:
            return "micas"
        if "fmt.com.mt/" in url:
            return "tnd"
        if "maltaorchestra.com/" in url:
            return "malta_orchestra"
        if "www.artsweven.com/" in url:
            return "arts_weven"
        if "ziguzajg.org/" in url:
            return "ziguzajg"
        if "heartofgozo.org.mt/" in url:
            return "heart_of_gozo"
        if "teatruaurora.com/" in url:
            return "teatru_aurora"
        if "worldofmalta.com/" in url:
            return "world_of_malta"
        if "showshappening.com/" in url:
            return "shows_happening"
        if "ticketline.com.mt/" in url:
            return "ticketline"

    def populate_links(self, events_links, sources_events_links, limit_links=15):
        for source in sources_events_links:
            if len(sources_events_links[source]) == 0:
                print(f"Sources Events Links is Empty ({source})")
                return

            # print(f"SOURCE: {source}")
            try:
                self.driver.get(self.sources_page_links[source])
            except TimeoutException:
                print(f"Timeout occurred while trying to access {self.sources_page_links[source]}")
                continue  # Continue to the next source if timeout occurs

            try:
                # Wait for links to be present using WebDriverWait
                links = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, sources_events_links[source]))
                )
                links = links[:limit_links]  # Limit the number of links to process

                print(f"Number of Links at {source}: {len(links)}")

                for l in links:
                    try:
                        href = l.get_attribute("href")
                        if href:
                            events_links.add(href)
                    except Exception as e:
                        print(f"Error while retrieving href attribute: {e}")
                        continue

            except TimeoutException:
                print(f"Timeout occurred while waiting for elements from {source}")

                # Try the rest of the elements

        

        return events_links

    def save_to_csv(self, events_links, filename, filetype=".csv"):
        events_links.to_csv(f"{filename+filetype}", sep=",", encoding='utf-8', index=False)

    def save_as_txt(self, list_:list, filename:str):
        with open(filename, 'w+', encoding='utf-8') as f:
            for item in list_:
                f.write(item)

        print("🟢 List saved to", filename)

    def read_txt_file(self, filename):
        list_ = []
        with open(filename, 'r+', encoding='utf-8') as f:
            for line in f:
                list_.append(line.rstrip("\n"))

        return list_

   
    def events_by_xpaths(self, driver, xpaths):
        print(f"🔴🔴🔴🔴 Scraping Event from {driver.current_url}")
        # sleep(2)

        try:
            event_details = {}

            for key, xpath in xpaths.items():
                if xpath:  # Only process non-empty XPath values
                    element = None
                    if "ziguzajg.org" in driver.current_url:
                        # Check if there is <h1 class="elementor-heading-title elementor-size-default">This event has passed</h1>
                        if "This event has passed" in driver.page_source:
                            return None

                    try:
                        element = WebDriverWait(driver, ELEMENT_WAIT).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                    except NoSuchElementException:
                        print(f"Element not found: {xpath}")
                        element = None
                        event_details[key] = ""
                        continue
                    except TimeoutException:
                        print(f"Timeout occurred while waiting for element: {xpath}")
                        event_details[key] = ""

                    # Multiple elements
                    if element or "micas.art" in driver.current_url:
                        if "zfinmalta.org" in driver.current_url:
                            if key == "fee":
                                # Concatenate all fee elements
                                fee_elements = driver.find_elements(By.XPATH, xpath)
                                fee = ""
                                for f in fee_elements:
                                    fee += f.text.strip() + ", "

                                # Remove last comma
                                fee = fee[:-2]

                                event_details[key] = fee
                            else:
                                event_details[key] = element.text.strip()
                        elif "micas.art" in driver.current_url:
                            if key == "title":
                                # Get web page title
                                event_details[key] = driver.title
                            elif element:
                                event_details[key] = element.text.strip()
                            else:
                                event_details[key] = ""

                        else:
                            event_details[key] = element.text.strip()
                                
                    else:
                        event_details[key] = ""


                    # Value splitting
                    if "teatrumanoel.mt" in driver.current_url:
                        if key == "time":
                            # substring after AT
                            event_details[key] = event_details[key].upper().split("AT")[1].strip()
                    
                    if "kreattivita.org" in driver.current_url:
                        if key == "date":
                            # substring before @
                            if "@" in event_details[key]:
                                event_details[key] = event_details[key].split("@")[0].strip()
                        elif key == "time":
                            # substring after @
                            if "@" in event_details[key]:
                                event_details[key] = event_details[key].split("@")[1].strip()
                            else:
                                event_details[key] = ""

                    if "micas.art" in driver.current_url:
                        if key == "date":
                            event_details[key] = event_details[key].split(":")[-1].strip()
                        elif key == "time":
                            if "Time" in event_details[key]:
                                event_details[key] = event_details[key].split("Time:")[-1].strip()
                            elif "TIME" in event_details[key]:
                                event_details[key] = event_details[key].split("TIME:")[-1].strip()
                        elif key == "location":
                            if "Venue" in event_details[key]:
                                event_details[key] = event_details[key].split("Venue:")[-1].strip()
                            elif "VENUE" in event_details[key]:
                                event_details[key] = event_details[key].split("VENUE:")[-1].strip()

                    if "www.zfinmalta.org" in driver.current_url:
                        if key == "date":
                            # substring before @
                            event_details[key] = event_details[key].split("@")[0].strip()
                        elif key == "time":
                            # substring after @
                            event_details[key] = event_details[key].split("@")[1].strip()

                    if "www.fmt.com.mt" in driver.current_url:
                        if key == "time":
                            # substring after AT
                            event_details[key] = event_details[key].split(",")[1].strip()

                    if "maltaorchestra.com" in driver.current_url:
                        if key == "location":
                            if ':' in event_details[key]:
                                event_details[key] = event_details[key].split(":")[-1].strip()

                    if "ziguzajg.org" in driver.current_url:
                        if key == "date":
                            if 'Programme' or 'School Shows' in event_details[key]:
                                event_details[key] = ""
                            elif '–' in event_details[key]:
                                event_details[key] = event_details[key].split(" at ")[0].strip()[2:]
                            else:
                                # substring after AT
                                event_details[key] = event_details[key].split(" at ")[0].strip()
                        if key == "time":
                            # substring after AT
                            if 'at' in event_details[key]:
                                event_details[key] = event_details[key].split(" at ")[-1].strip()
                            elif ',' in event_details[key]:
                                event_details[key] = event_details[key].split(",")[-1].strip()
                            else:
                                if 'Programme' or 'School Shows' in event_details[key]:
                                    event_details[key] = ""
                                else:
                                    event_details[key] = event_details[key].strip()

                    if "heartofgozo.org.mt" in driver.current_url:
                        if key == "location":
                            event_details[key] = event_details[key].split(",")[0].strip()
                        if key == "time":
                            event_details[key] = event_details[key].split("|")[1].strip()
                            
                    if "showshappening.com" in driver.current_url:
                        if key == "date":
                            if 'at' in event_details[key]:
                                event_details['time'] = event_details[key].split(" at ")[-1].strip()
                                event_details[key] = event_details[key].split(" at ")[0].strip()


                    if "teatruaurora.com" in driver.current_url:
                        if key == "date":
                            event_details[key] = event_details[key].split("-")[-1].strip()

                    if "ticketline.com" in driver.current_url:
                        if key == "date":
                            event_details[key] = event_details[key].split(":")[-1].strip()
                        if key == "time":
                            # Find where "Time:" ends, take rest after
                            event_details[key] = event_details[key].split("Time:")[-1].strip()
                            # pass

            e = Inkontru_Event()

            e.event_name = event_details.get('title', '')

            if event_details.get('other_dates', '') == "":
                e.dates = event_details.get('date', '')
            else:
                e.dates = event_details.get('other_dates', '')

            e.location = event_details.get('location', '')
            e.time = event_details.get('time', '')
            e.duration = event_details.get('duration', '')
            e.audience_level = event_details.get('audience_level', '')
            e.fee = event_details.get('fee', '')
            e.link = driver.current_url

            return e

        except Exception as exc:
            # Handle other exceptions gracefully
            print(f"🔴 Error occurred during scraping link {driver.current_url}: {exc}")
            print(f'Current key is: {key}')
            sleep(2)
            return e

    def scrape_events(self, driver, source):
    # if "teatrumalta" in driver.current_url or "festivals" in driver.current_url: # or
        return self.events_by_xpaths(driver, self.scrape_events_xpaths[source])
