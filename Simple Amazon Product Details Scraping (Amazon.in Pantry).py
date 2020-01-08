#!/usr/bin/env python
# coding: utf-8

# ### Scraping product details from Amazon.in Pantry: Considering products from first page of search results for a specific search term
# Search term: "coca cola" 
# Amazon website: "amazon.in"
# 
# ##### Process Used:
# 1. Use Selenium to open Google
# 2. Search for amazon website
# 3. Go to amazon home page
# 4. Search for product
# 5. Scrape product details from the search results page
# 6. Save outputs as an excel
# 
# ##### Callouts:
# 1. Have used Selenium and used google as the website (amazon) entry point, to avoid getting flagged as an automated bot
# 2. Have also used explicit delays between tasks, to mimic human behaviour

# In[92]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from bs4 import BeautifulSoup
import pandas as pd
import time

def get_product_details_from_amazon(amazon_search_term):
    # This example requires Selenium WebDriver 3.13 or newer
    # Chromedriver must be in the PATH variable
    driver = webdriver.Chrome()
    # 0. Open Chrome browser and wait for it to load
    wait = WebDriverWait(driver, 10)

    # 1. Open Google and Search for amazon website and wait for 5 seconds
    driver.get("https://google.com/ncr")
    driver.find_element_by_name("q").send_keys("amazon pantry india" + Keys.RETURN)
    time.sleep(3)

    # 2. Click on the first result that will lead to amazon website
    first_result = wait.until(presence_of_element_located((By.XPATH, "//div[@class='r']/a")))
    #wait.until(presence_of_element_located((By.CSS_SELECTOR, "h3>div")))
    #print(first_result.get_attribute("textContent"))
    first_result.click()

    # 3. Wait for 4 seconds after opening amazon website and search for product
    time.sleep(4)
    driver.find_element_by_id("twotabsearchtextbox").send_keys(amazon_search_term)
    time.sleep(1)
    driver.find_element_by_id("twotabsearchtextbox").send_keys(Keys.RETURN)
    time.sleep(2)

    # 4. Parse the search results using beautiful soup and get product details
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    search_results_soup = soup.find_all(attrs={"class": ['s-result-list', 's-search-results sg-row']})[0].findAll('div', attrs = {'data-asin' : True})
    search_results_df = pd.DataFrame()
    for search_result in search_results_soup:
        # Error prone attributes
        price = ''
        rating = ''
        number_of_ratings= ''
        price_currency=''
        original_price = ''
        try:
            price = search_result.find(attrs={"class": 'a-price-whole'}).get_text()
            price_currency = search_result.find(attrs={"class": 'a-price-symbol'}).get_text()
            rating = search_result.find('div', attrs={'class': 'a-row a-size-small'}).find('span',attrs = {'aria-label' : True})['aria-label']
            number_of_ratings = search_result.find('div', attrs={'class': 'a-row a-size-small'}).find_all('span',attrs = {'aria-label' : True})[1]['aria-label']
            original_price = search_result.find_all('span', attrs={'class': 'a-offscreen'})[1].get_text()
        except AttributeError:
            pass
        except IndexError:
            pass
        search_results_df = search_results_df.append({'asin':  search_result['data-asin'],
                                                      'price':  price,
                                                      'price_currency': price_currency,
                                                      'original_price': original_price,
                                                      'rating':  rating,
                                                      'number_of_ratings':  number_of_ratings,
                                                      'product_name':  search_result.find('h2').text.strip(),
                                                      'product_url':  search_result.find('h2').a['href'],
                                                      'search_page_url': driver.current_url,
                                                      'search_term': amazon_search_term,
                                                      'amazon_choice_flag':  'amazons-choice' in str(search_result.find('span',attrs={'class': 'rush-component','data-component-props': True}))
                                                     }, ignore_index=True)
    time.sleep(4)
    driver.close()
    return search_results_df


# In[98]:


search_term = "coca cola"
search_results_df = get_product_details_from_amazon(search_term)
search_results_df.to_excel("Amazon.in Pantry Search Results for Coca Cola (Only Page 1).xlsx")


# In[99]:


search_results_df

