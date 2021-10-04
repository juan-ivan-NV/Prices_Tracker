import os
import time
# pip install selenium
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup # pip install beautifulsoup4
import pandas as pd # pip install pandas

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'
FireFoxDriverPath = os.path.join(os.getcwd(), 'Drivers', 'geckodriver.exe')
FireFoxProfile = webdriver.FirefoxProfile()
FireFoxProfile.set_preference("general.useragent.override", user_agent)
url = "https://www.ebay.com/"
browser = webdriver.Firefox(executable_path=FireFoxDriverPath)
browser.implicitly_wait(7)
browser.get(url)

search_keyword = 'Playstation 5'
search_field = browser.find_element_by_id('gh-ac')
search_field.clear()
search_field.send_keys(search_keyword)
search_field.send_keys(Keys.ENTER)

total_result = int(browser.find_element_by_class_name('srp-controls__count-heading').find_element_by_class_name('BOLD').text.replace(',', ''))
ebay_listings = []

current_page = 1
to_continue = True

while to_continue:
    try:
        print('Processing page {0}'.format(current_page))

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        item_list = soup.find_all('li', 's-item--watch-at-corner')
        
        for listing in item_list:
            product_detail = {}

            product_detail['product title'] = listing.h3.text
            product_detail['product url'] = listing.a['href']
            
            listing_subtitles = listing.find_all('div', 's-item__subtitle')
            if len(listing_subtitles) == 2:
                listing_subtitle_1 = listing_subtitles[0].text
                listing_subtitle_2 = listing_subtitles[1].text
            elif len(listing_subtitles) == 1:
                listing_subtitle_1 = listing_subtitles[0].text
                listing_subtitle_2 = None
            else:
                listing_subtitle_1 = None
                listing_subtitle_2 = None

            product_detail['subtitle1'] = listing_subtitle_1
            product_detail['subtitle2'] = listing_subtitle_2


            # Star rating and product review count
            try:
                x_star_rating = listing.find('div', 'x-star-rating')
                stars = len(x_star_rating.find_all('svg', 'icon--star-filled-small'))
                review_count = int(listing.find('span', 's-item__reviews-count').span.text.replace( ' product ratings', ''))
                
                product_detail['stars'] = stars
                product_detail['product review_count'] = review_count
            except Exception as e:
                product_detail['stars'] = ''
                product_detail['product review_count'] = ''

            product_detail['price'] = listing.find('span', 's-item__price').text

            try:
                product_detail['shipping detail'] = listing.find('span', 's-item__logisticsCost').text
            except AttributeError:
                product_detail['shipping detail'] = 'Not Available'
                
            ebay_listings.append(product_detail)


        time.sleep(1)
        browser.find_element_by_xpath('//a[@class="pagination__item" and text()="{0}"]'.format(current_page+1)).click()
        current_page +=1

        if current_page > 5:
            raise Exception('Stop')

    except NoSuchElementException:
        print('Last page {0}'.format(current_page))
        to_continue = False


df = pd.DataFrame(ebay_listings)
df.to_excel('playstation 5 listings.xlsx', index=False)