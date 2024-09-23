import sys
import os

from Scraper import Scraper
import pandas as pd
import sheets

LINK_LIMIT = 15

def get_links(worksheet, data, column_index):
    data_links = [d[0] for d in data]
    scraper = Scraper(sources_page_links, sources_events_links)
    read_from_file = False

    if read_from_file:
        events_links = scraper.read_txt_file("events_links.txt")
    else:
        events_links = set()
        events_links = scraper.populate_links(events_links, sources_events_links, limit_links=LINK_LIMIT)

    # print("Events Links:", events_links)

    event_details = []
    count_ = 0 
    for e in list(events_links):
        if e in data_links:
            print(f"Link {e} already exists")
            continue
        
        # print(f"SCRAPING {e}")
        scraper.driver.get(e)
        source = scraper.get_source_from_url(scraper.driver.current_url)
        # print("Source:", source)
        event = scraper.scrape_events(scraper.driver, source)

        if not event or not event.link:
            continue

        event.entity = source
        event.show()
        event_list = event.as_dict()
        event_as_list = event.as_list()

        if event_list not in event_details:
            if not sheets.check_link_exists(event_as_list[0], data, column_index):
                count_ += 1
                sheets.add_data_as_list(worksheet, event_as_list, event.link)
                event_details.append(event_as_list)
            
    print(f"Added {count_} listings to sheet...")

    return event_details

if __name__ == "__main__":
    # get links to source website
    sources_page_links = {
        "festivals_malta" : "https://www.festivals.mt/what-s-on",
        "teatru_manoel" : "https://teatrumanoel.mt/whats-on/",
        "teatru_malta" : "https://teatrumalta.org.mt/programme/?lang=en",
        "zfin_malta" : "https://www.zfinmalta.org/events/",
        "kreattivita" : "https://www.kreattivita.org/en/event/",
        "micas" : "https://micas.art/events/",
        "tnd" : "https://www.fmt.com.mt/tnd/",
        "malta_orchestra" : "https://maltaorchestra.com/calendar-of-events/",
        # "arts_weven" : "https://www.artsweven.com/",
        "ziguzajg" : "https://www.ziguzajg.org/", ## working
        "heart_of_gozo" : "https://heartofgozo.org.mt/events-exhibitions/",
        "teatru_aurora" : "https://teatruaurora.com/upcoming-events/",
        # "world_of_malta" : "https://worldofmalta.com/en/events/",
        "shows_happening" : "https://www.showshappening.com/search",
        "ticketline" : "https://www.ticketline.com.mt/Events.aspx"
        }

    # get links to event pages
    sources_events_links = {
        "festivals_malta" : "//*[contains(@href, 'festivals.mt/what-s-on/')]", ## working
        "teatru_manoel" : "//*[contains(@href, 'https://teatrumanoel.mt/event/')]", ## only loads first 3 links
        "teatru_malta" : "//*[contains(@href, 'teatrumalta.org.mt/events/')]", ## working
        "zfin_malta" : "//*[contains(@href, 'www.zfinmalta.org/event/')]", ## working
        "kreattivita" : "//*[contains(@href, 'en/event/') and not(contains(@href, '/all')) and substring-after(@href, 'en/event/') != '']", ## working
        "micas" : "//*[contains(@href, '/events/') and not(contains(@href, '/feed')) and not(@href = 'https://micas.art/events/') and not(@href = 'https://micas.art/mt/events/')]", ## no current events
        # "tnd" : "//*[contains(@href, '/event-details/')]", ## working
        "tnd" : "//*[contains(@href, '/event-details/') and not(contains(@href, 'facebook')) and not(contains(@href, 'twitter'))]",
        "malta_orchestra" : "//*[contains(@href, '/events/')]", ## working but location is ambiguous
        # "arts_weven" : "", ## does not have event pages
        "ziguzajg" : "//*[contains(@href, 'ziguzajg.org/') and contains(@class, 'elementor-button')]", ## working but includes old events 
        "heart_of_gozo" : "//*[contains(@href, 'heartofgozo.org.mt/events/')]", # working, keep close eye
        "teatru_aurora" : "//*[contains(@href, 'teatruaurora.com') and contains (@class, 'mkdf-fsgi-link')]", ## working, keep close eye as the page is in development
        # "world_of_malta" : "", ## this site is a mess
        "shows_happening" : "//a[contains(@href, 'showshappening') and contains(@class, 'event_small_cards')]", ## working
        "ticketline" : "//*[contains(@href, 'bookings/')]"
    }

    
    sheet_name = "inkontru-scraper"
    worksheet_name = "DATA"
    data_range = "A2:I"
    column_index = 0

    sheet = sheets.open_sheet(sheet_name)
    worksheet = sheets.open_worksheet(sheet, worksheet_name)

    data = sheets.read_sheet(worksheet, data_range)
    existing_event_links = [d[column_index] for d in data]

    print(f"Existing Event Links: {len(existing_event_links)}")

    events_ = get_links(worksheet, data, column_index)
    print("Added events:", [i[0] for i in events_])
