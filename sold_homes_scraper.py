"""
sold_homes_scraper.py

The file uses a function called scrape_5_houses repeatedly to scrape info from sold homes on homes.com. 
It uses a package called playwright to open a browser and website, mimicing human behavior, in order to dodge 
blocking. playwright is also used to select information from the html/js. scrape_5_houses produces a .csv file 
with 5 houses info. To loop through all homes, the scrape_all function is used. The scrape_all function uses 
4 separate processes which each call scrape_5_houses individually to increase speed. While running, a message 
prints indicating what house number out of 40 on the page is being scraped, as well as a completed step message 
for every 20 houses scraped, prompting the user to switch VPN locations to prevent being blocked. Everytime a 
page is completed,the 8 individual .csv files with 5 houses are combined into one. The final product will be 
one .csv file per page.

Notes for use: Alter URL builder if interested in non buncombe county houses. May need to check that the
4 price bins obey the 720 house limit on homes.com. The script is not capable of handling the final page of a 
homes.com search at the moment, since it expects 40 houses per page. Make sure to change VPN locations every
20 houses.

Author: Andrew Smith
Date: July 2025
"""

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError
import pandas as pd
import math
import csv
import random
import time
import multiprocessing
import os


def scrape_5_houses(price_range,page,eighth):
    """
    Goes to homes.com's sold single family homes in buncombe county and scrapes all available data. Produces
    a .csv file with 5 homes information.

    Args: 
        price_range (int): Sets a price filter on homes.com. This is necessary because homes.com will only
            show up to 720 homes at once, even if more are available, thus 4 price buckets are 
            used at the time of writing this for the 2300 homes. 
        page (int): Which page of homes to scrape.
        eighth (int): Which eighth of the 40 homes to scrape.
    """
    #name of csv that will be written
    csv_title = f"{price_range}_{page}_{eighth}_homes.csv"

    #which of the 40 houses to scrape
    start = (eighth-1)*5
    end = eighth*5

    #url builder
    if price_range == 1:
        price_ext = '/?property_type=1&price-max=429999'
    elif price_range == 2:
        price_ext = '/?property_type=1&price-min=430000&price-max=629999'
    elif price_range == 3:
        price_ext = '/?property_type=1&price-min=629999&price-max=999999'
    else:
        price_ext = '/?property_type=1&price-min=1000000'

    if page == 1:
        page_ext = ''
    else:
        page_ext = f'/p{page}'

    BASE_MAIN_LINK = 'https://www.homes.com/buncombe-county-nc/sold'
    MAIN_LINK = f"{BASE_MAIN_LINK}{page_ext}{price_ext}"
    BASE_INDIVIDUAL_LINK = 'https://www.homes.com'

    #variable lists for csv rows
    address_list = []
    price_list = []
    days_on_market_list = []
    sq_ft_list = []
    price_per_sq_ft_list = []
    beds_list = []
    baths_list = []
    year_built_list = []
    airport_commute_list = []
    crime_score_list = []
    walk_score_list = []
    sound_score_list = []
    flood_score_list = []
    fire_score_list = []
    heat_score_list = []
    wind_score_list = []
    air_score_list = []
    elem_school_list = []
    elem_score_list = []
    elem_commute_list = []
    middle_school_list = []
    middle_score_list = []
    middle_commute_list = []
    high_school_list = []
    high_score_list = []
    high_commute_list = []
    url_list = []

    #create csv
    with open(csv_title, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['address', 'price', 'days on market','sqft','price per sqft','beds', 'baths', 'year built', 'airport commute','crime score','walkability','sound score','flood score','fire score','heat score','wind score','air score','elem. school','elem. niche','elem. commute','middle school','middle niche','middle commute','high school','high school niche','high school commute','url'])

        #start playwright
        with sync_playwright() as p:
            #open browser and webpage
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(MAIN_LINK)
            time.sleep(random.uniform(3, 10))

            #locates each house container of the 40 available on the main page
            placards = page.locator('li.placard-container')

            #loop through the eighth of placards and extract data
            for i in range(start,end):
                #print current house to track progress
                print(i)

                placard = placards.nth(i)
                info1 = placard.locator('ul.detailed-info-container.sqft-container li')
                info2 = placard.locator('ul.detailed-info-container:not(.sqft-container) li')

                #append info that is contained on the main page
                try:
                    address = placard.locator('p.property-name').inner_text()
                    address_list.append(address)
                except:
                    address_list.append(None)

                try:
                    raw_price = placard.locator('p.price-container').inner_text()
                    price_only = raw_price.split("SOLD")[0].strip().replace("$", "").replace(",", "")
                    price_list.append(int(price_only))
                except:
                    price_list.append(None)

                try:
                    sq_ft = info1.nth(0).inner_text()
                    sq_ft_number = ''.join(filter(str.isdigit, sq_ft))
                    sq_ft_list.append(int(sq_ft_number))
                except: 
                    sq_ft_list.append(None)

                try: 
                    price_per_sq_ft = info1.nth(1).inner_text()
                    price_per_sq_ft_number = ''.join(filter(str.isdigit, price_per_sq_ft))
                    price_per_sq_ft_list.append(int(price_per_sq_ft_number))
                except:
                    price_per_sq_ft_list.append(None)

                try:
                    days_on_market = info1.nth(2).inner_text()
                    days_only = ''.join(filter(str.isdigit, days_on_market))
                    days_on_market_list.append(int(days_only))
                except:
                    days_on_market_list.append(None)

                try:
                    beds = info2.nth(0).inner_text()
                    beds_num = ''.join(filter(str.isdigit, beds))
                    beds_list.append(int(beds_num))
                except:
                    beds_list.append(None)

                try:
                    baths = info2.nth(1).inner_text()
                    baths_num = ''.join(filter(str.isdigit, baths))
                    if float(baths_num) > 10:
                        baths_list.append(float(baths_num)/10)
                    else:
                        baths_list.append(float(baths_num))
                except:
                    baths_list.append(None)

                try:
                    year_built = info2.nth(2).inner_text()
                    year_num = ''.join(ch for ch in year_built if ch.isdigit())
                    year_built_list.append(int(year_num))
                except:
                    year_built_list.append(None)

                href_container = placard.locator('a[href^="/property/"]')
                href = href_container.first.get_attribute('href')
                url = f"{BASE_INDIVIDUAL_LINK}{href}"
                url_list.append(url)


                #go to individual link to get the rest of the info
                page.goto(url)
                time.sleep(random.uniform(3, 5))

                # Scroll through the page to load JavaScript-rendered content
                scroll_height = page.evaluate("document.body.scrollHeight")
                rounded_height = math.floor(scroll_height / 30) * 30
                step = rounded_height // 30

                # Scroll until the schools card is visible
                for j in range(0, rounded_height, step):  
                    page.evaluate(f"window.scrollTo(0, {j})")
                    try:
                        if page.locator(".school-card-container.school-in-area-container").first.is_visible():
                            break  # Exit when school section appears
                    except:
                        pass
                    page.wait_for_timeout(500)  # Slight delay between scrolls


                #try to wait for the airport variable to be visible, then extract info
                try:
                    page.wait_for_selector(".transportation-item:has-text('Asheville Regional')")
                    airport = page.locator('.transportation-item').filter(has_text='Asheville Regional')

                    airport_commute = airport.locator('.transportation-distance').inner_text()
                    minutes = ''.join(ch for ch in airport_commute if ch.isdigit())
                    airport_commute_list.append(int(minutes))

                except TimeoutError:
                    airport_commute_list.append(None)

                #try to wait for the area variables to be visible, then extract info
                try:
                    page.wait_for_selector("#score-card-container")

                    if page.locator(".crime-score .score-scoretext").is_visible():
                        crime_score = page.locator(".crime-score .score-scoretext").inner_text()
                        crime_score_list.append(crime_score)
                    else:
                        crime_score_list.append(None)

                    if page.locator(".walk-score .score-scoretext").is_visible():
                        walk_score = page.locator(".walk-score .score-scoretext").inner_text()
                        walk_score_list.append(walk_score)
                    else:
                        walk_score_list.append(None)
                    
                except TimeoutError:
                    crime_score_list.append(None)
                    walk_score_list.append(None)

                #try to wait for the environmental variables to be visible, then extract info
                try:
                    page.wait_for_selector("#environment-factor-container")

                    #extract and store environmental variables
                    environmental_info = page.locator("#environment-factor-container .score-card")
                    environmental_size = environmental_info.count()
                    sound_bool = flood_bool = fire_bool = heat_bool = wind_bool = air_bool = False

                    for j in range(environmental_size):
                        factor = environmental_info.nth(j)
                        title = factor.locator(".score-card-title").inner_text().strip()
                        score = factor.locator(".score-scoretext").inner_text().strip()

                        if("Sound" in title):
                            sound_score_list.append(score)
                            sound_bool = True
                        elif("Flood" in title):
                            flood_score_list.append(score)
                            flood_bool = True
                        elif("Fire" in title):
                            fire_score_list.append(score)
                            fire_bool = True
                        elif("Heat" in title):
                            heat_score_list.append(score)
                            heat_bool = True
                        elif("Wind" in title):
                            wind_score_list.append(score)
                            wind_bool = True
                        elif("Air" in title):
                            air_score_list.append(score)
                            air_bool = True
                        
                    if(not sound_bool):
                        sound_score_list.append(None)
                    if(not flood_bool):
                        flood_score_list.append(None)
                    if(not fire_bool):
                        fire_score_list.append(None)
                    if(not heat_bool):
                        heat_score_list.append(None)
                    if(not wind_bool):
                        wind_score_list.append(None)
                    if(not air_bool):
                        air_score_list.append(None)
                except TimeoutError:
                    sound_score_list.append(None)
                    flood_score_list.append(None)
                    fire_score_list.append(None)
                    heat_score_list.append(None)
                    wind_score_list.append(None)
                    air_score_list.append(None)
                
                #try to wait for the schools and extract info
                try:
                    elem_bool = middle_bool = high_bool = False
                    page.wait_for_selector(".school-card-container.school-in-area-container")
                    school_names = []
                    school_grades = []
                    commute_time = []
                    current_cards = page.locator(".school-card-container.school-in-area-container")
                    for j in range(current_cards.count()):
                        name = current_cards.nth(j).locator(".school-name").inner_text()
                        school_names.append(name)
                        try:
                            grade = current_cards.nth(j).locator(".score-1 span").inner_text(timeout=3000)
                            school_grades.append(grade)
                        except:
                            school_grades.append(None)
                        try: 
                            commute_raw = current_cards.nth(j).locator(".walk-drive-time").inner_text()
                            if "drive" in commute_raw:
                                commute = int(commute_raw.split()[0])
                            elif "walk" in commute_raw:
                                commute = 1 
                            else:
                                commute = None 
                            commute_time.append(commute)
                        except:
                            commute_time.append(None)
                        
                    for index in range(len(school_names)):
                        if ("Elementary" in school_names[index]) and (not elem_bool):
                            elem_school_list.append(school_names[index])
                            elem_score_list.append(school_grades[index])
                            elem_commute_list.append(commute_time[index])
                            elem_bool = True
                        elif ("Middle" in school_names[index]) and (not middle_bool):
                            middle_school_list.append(school_names[index])
                            middle_score_list.append(school_grades[index])
                            middle_commute_list.append(commute_time[index])
                            middle_bool = True
                        elif ("High" in school_names[index]) and (not high_bool):
                            high_school_list.append(school_names[index])
                            high_score_list.append(school_grades[index])
                            high_commute_list.append(commute_time[index])
                            high_bool = True

                    if not elem_bool:
                        elem_school_list.append(None)
                        elem_score_list.append(None)
                        elem_commute_list.append(None)
                    if not middle_bool:
                        middle_school_list.append(None)
                        middle_score_list.append(None)
                        middle_commute_list.append(None)
                    if not high_bool:
                        high_school_list.append(None)
                        high_score_list.append(None)
                        high_commute_list.append(None)

                except TimeoutError:
                    elem_school_list.append(None)
                    elem_score_list.append(None)
                    elem_commute_list.append(None)
                    middle_school_list.append(None)
                    middle_score_list.append(None)
                    middle_commute_list.append(None)
                    high_school_list.append(None)
                    high_score_list.append(None)
                    high_commute_list.append(None)

                #return to the main page
                page.goto(MAIN_LINK)
                time.sleep(random.uniform(3, 5))

            #after looping through 5 houses, write all rows to the csv
            for l in range(len(address_list)):
                writer.writerow([address_list[l],price_list[l],days_on_market_list[l],sq_ft_list[l],price_per_sq_ft_list[l],beds_list[l],baths_list[l],year_built_list[l],airport_commute_list[l],crime_score_list[l],walk_score_list[l],sound_score_list[l],flood_score_list[l],fire_score_list[l],heat_score_list[l],wind_score_list[l],air_score_list[l],elem_school_list[l],elem_score_list[l],elem_commute_list[l],middle_school_list[l],middle_score_list[l],middle_commute_list[l],high_school_list[l],high_score_list[l],high_commute_list[l],url_list[l]])

            browser.close()
            return
        

def scrape_all(price_range,page_start,page_end,skip_first_half):
    """
    Loops through each page prompted by the user, scraping housing data. Each page of 40 houses is split into two 
    loops, so 20 houses are dealt with at a time. There are 4 processes that each run scrape_5_houses individually. 
    After process completion, each individual .csv file is combined into one, and a two minute break is taken to 
    prevent getting blocked. VPN location must be changed at this time. The end product is however many pages the
    user input worth of .csv files.

    Args: 
        price_range (int): A value between 1 and 4 that indicates which price range filter for scrape_5_houses
            to use.
        page_start (int): Which page of homes to begin scraping at.
        page_end (int): Which page of homes to end scraping at (exclusive).
        skip_first_half (boolean): Indicates whether the first half of homes on the starting page should be 
            skipped. This is necessary because sometimes the program will crash in the second half of the loop.
    """
    if __name__ == "__main__":
        for page in range(page_start,page_end):
            #keep track of individual .csv titles so they can be deleted later after being concatenated
            csv_titles = []
            #since there are 4 processes that each handle 5 houses, loop through twice
            for half in range(2):
                if (skip_first_half) & (page == page_start) & (half==0):
                    csv_titles.append(f"{price_range}_{page_start}_1_homes.csv")
                    csv_titles.append(f"{price_range}_{page_start}_2_homes.csv")
                    csv_titles.append(f"{price_range}_{page_start}_3_homes.csv")
                    csv_titles.append(f"{price_range}_{page_start}_4_homes.csv")
                    continue
                processes = []
                p1 = multiprocessing.Process(target=scrape_5_houses,args=[price_range,page,(1+(4*half))])
                processes.append(p1)
                csv_titles.append(f"{price_range}_{page}_{(1+(4*half))}_homes.csv")
                p2 = multiprocessing.Process(target=scrape_5_houses,args=[price_range,page,(2+(4*half))])
                processes.append(p2)
                csv_titles.append(f"{price_range}_{page}_{(2+(4*half))}_homes.csv")
                p3 = multiprocessing.Process(target=scrape_5_houses,args=[price_range,page,(3+(4*half))])
                processes.append(p3)
                csv_titles.append(f"{price_range}_{page}_{(3+(4*half))}_homes.csv")
                p4 = multiprocessing.Process(target=scrape_5_houses,args=[price_range,page,(4+(4*half))])
                processes.append(p4)
                csv_titles.append(f"{price_range}_{page}_{(4+(4*half))}_homes.csv")

                for p in processes:
                    p.start()

                for p in processes:
                    p.join()

                #progress message, must wait 2 mins to prevent blocking
                print(f"Completed step {half+1} for page {page}. Change VPN locations.")
                time.sleep(120)

                #combine individual .csv files if both loops are completed
                if half == 1:
                    combined_df = pd.concat([pd.read_csv(file) for file in csv_titles], ignore_index=True)
                    combined_df.to_csv(f"{price_range}_{page}.csv", index=False)
                    for file in csv_titles:
                        os.remove(file)



