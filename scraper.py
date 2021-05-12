# Code borrowed from:
# https://www.edureka.co/blog/web-scraping-with-python/
# Notes: I was able to extract the image urls for each image in the results
# HOWEVER, for some reason if the url is similar to the following:
# https://rovimusic.rovicorp.com/image.jpg?c=WMK1lwcbiDVczs9qEos9vipQg_7iAU1wjqLgK_xGXts=&amp;f=1
# then on attempt to load, chrome throws an "invalid request", which makes no sense because this
# only occurs in the script. If I manually open the page, inspect elements, and go to an image url
# of that type, the image successfully loads. Furthermore, only at most 3-4 images out of the ~20
# images per page are not of that type.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from PIL import Image
import time
import requests
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
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'cookie-policy-box'))
)
#driver.find_elements_by_xpath("//input[@name='recording-type' and @value='Main Albums']")[0].click()
element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='recording-type' and @value='Main Albums']"))
        )
#driver.implicitly_wait(20)
element.click()

page = 0
while True:
    page += 1
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'cover'))
    )
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    # print(soup)
    results = soup.find_all("tr")
    for album in results:
        stringToParse = str(album)
        albumIndToStart = stringToParse.find("data-original")
        if albumIndToStart == -1:
            continue
        albumIndToEnd = stringToParse.find(' ', albumIndToStart)
        coverUrl = stringToParse[albumIndToStart+15:albumIndToEnd-1]
        if coverUrl.find('f=1') != -1:
            continue
        print(coverUrl)
        img_urls.append(coverUrl)

        albumTitleIndStart = stringToParse.find('e">\n<a href="')
        if albumTitleIndStart == -1:
            print("THIS SHOULDN'T HAPPEN")  # every album should contain this url
            continue
        albumTitleIndEnd = stringToParse.find('">', albumTitleIndStart+3)
        titleUrl = stringToParse[albumTitleIndStart+13:albumTitleIndEnd]
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(titleUrl)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'genre'))
        )
        genreSoup = BeautifulSoup(driver.page_source, 'html.parser')
        genreText = str(genreSoup.find("div", "genre"))
        genreTextIndEnd = genreText.find('</a')
        genreTextIndStart = genreText.rfind('>', 0, genreTextIndEnd)
        genre = genreText[genreTextIndStart+1:genreTextIndEnd]
        print(genre)
        genres.append(genre)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        #print(Image.open(requests.get(url, stream=True).raw))

    #for album in soup.find_all("tr"):
    #    img_urls.append(album.get('src'))

    #print(img_urls)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "next"))
        )
        element.click()
        pass
    except:
    #    print("Page: "+str(page))
    #    break
        break





driver.close()

# TODO:
# Loop through each page
# For each image:
# If img class == "lazy" skip
# Else
#   store cropped img
#   go to title, click href, store genre


