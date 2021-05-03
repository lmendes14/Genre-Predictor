# Code borrowed from:
# https://www.edureka.co/blog/web-scraping-with-python/

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--test-type')
options.add_argument('load-extension=~/Downloads/adblock')
driver = webdriver.Chrome("/Users/lorenzomendes/Downloads/chromedriver", options=options)

img_urls = []
genres = []
# Open AllMusic advanced-search
driver.get("https://www.allmusic.com/advanced-search")

# Click on Main Albums
driver.implicitly_wait(10)
#driver.find_elements_by_xpath("//input[@name='recording-type' and @value='Main Albums']")[0].click()
element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='recording-type' and @value='Main Albums']"))
        )
#driver.implicitly_wait(20)
element.click()

page = 0
while True:
    page += 1
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'cover'))
    )
    page_source = driver.page_source


    soup = BeautifulSoup(page_source, 'html.parser')
    # print(soup)
    print(soup.find_all("tr"))
    #for album in soup.find_all("tr"):
    #    img_urls.append(album.get('src'))

    #print(img_urls)

    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        #element = WebDriverWait(driver, 10).until(
            #EC.presence_of_element_located((By.CLASS_NAME, "next"))
        #)
        #element.click()
        pass
    except:
    #    print("Page: "+str(page))
    #    break
        pass
    break



driver.close()

# TODO:
# Loop through each page
# For each image:
# If img class == "lazy" skip
# Else
#   store cropped img
#   go to title, click href, store genre


