# Code borrowed from:
# https://www.edureka.co/blog/web-scraping-with-python/

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from PIL import Image
import numpy
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
csvCount = 1
albumCount = 0
# Sometimes when trying to click on Main Albums, the site's cookie policy box gets in the way, so we'll
# loop until it's clickable.
while True:
    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='recording-type' and @value='Main Albums']"))
        )
        element.click()
        break
    except:
        pass

page = 0
# Successfully saved albums up to page 85, so we'll continue on page 88 to avoid any potential duplicates.
while page < 87:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "next"))
    )
    element.click()
    page += 1
csvCount = page+1

# Main loop of the scraper. For each page on main albums, save each cover url, click on each album, and store the genre.
# When all albums on a given page have been stored, scroll down and click on the next page.
# After every 40 albums have been stored, open each url to get the image, convert to a numpy array, and store it as a
# 40 x 9075 matrix csv file along with the genres.
while True:
    page += 1
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'cover'))
    )
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    results = soup.find_all("tr")  # Each album is stored under the 'tr' tag
    for album in results:
        stringToParse = str(album)
        albumIndToStart = stringToParse.find("data-original")
        if albumIndToStart == -1:
            continue
        albumIndToEnd = stringToParse.find(' ', albumIndToStart)
        coverUrl = stringToParse[albumIndToStart+15:albumIndToEnd-1]
        albumIndToStart = coverUrl.find('&amp')
        if albumIndToStart != -1:
            # REMOVE AMP;
            coverUrl = coverUrl[:albumIndToStart+1] + coverUrl[albumIndToStart+5:]


        albumTitleIndStart = stringToParse.find('e">\n<a href="')
        if albumTitleIndStart == -1:
            print("THIS SHOULDN'T HAPPEN")  # every album should contain this url
            continue
        albumTitleIndEnd = stringToParse.find('">', albumTitleIndStart+3)
        titleUrl = stringToParse[albumTitleIndStart+13:albumTitleIndEnd]

        # Open a new tab and access each album's url to find the genre
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(titleUrl)

        count = 0
        genreDoesntExist = False
        # Try to find the genre given in the album's page. After 5 tries, set the genreDoesntExist flag
        while True:
            try:
                count += 1
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'genre'))
                )
                break
            except:
                # After trying to find the genre 5 times, we'll assume it doesn't exist, set flag
                if count == 5:
                    genreDoesntExist = True
                    break
        # If the genre doesn't exist, skip the current album
        if genreDoesntExist:
            continue

        # Parse the album's page for the genre
        genreSoup = BeautifulSoup(driver.page_source, 'html.parser')
        genreText = str(genreSoup.find("div", "genre"))
        genreTextIndEnd = genreText.find('</a')
        genreTextIndStart = genreText.rfind('>', 0, genreTextIndEnd)
        genre = genreText[genreTextIndStart+1:genreTextIndEnd]
        genreTestIndStart = genre.find('amp')
        if genreTestIndStart != -1:
            genre = genre[:genreTestIndStart]+genre[genreTestIndStart+4:]

        # After retrieving both the image url and genre, store each in their respective lists
        genres.append(genre)
        img_urls.append(coverUrl)

        # Close the current album's page and switch back into the results page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Store images and urls after 40 albums
        if len(genres) == 40:

            np_mat = numpy.empty((0, 9075))
            offset = 0
            for i in range(40):
                img_url = img_urls[i]
                print(img_url)

                # Encountered this problem where some images couldn't be flatted to 9075 integer values
                # If this happens, don't store the image, and delete its genre
                try:
                    image = Image.open(requests.get(img_url, stream=True).raw)
                    image = image.resize((55, 55))
                    np_img = numpy.array(image)
                    np_img = np_img.flatten()
                    np_mat = numpy.append(np_mat, np_img[numpy.newaxis, :], axis=0)
                except:
                    del genres[i-offset]
                    offset += 1
            np_mat = numpy.round(np_mat).astype(int)
            pd.DataFrame(numpy.array(genres)).to_csv("~/Genre-Predictor/genres"+str(csvCount)+".csv")
            numpy.savetxt("covers"+str(csvCount)+".csv", np_mat, delimiter=",")
            csvCount += 1
            genres.clear()
            img_urls.clear()

    # Try to go to the next results page. After 5 tries, we'll assume we've reached the last page
    count = 0
    nextNotFound = False
    while (True):
        try:
            count += 1
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "next"))
            )
            element.click()
            break
        except:
            if count == 5:
                nextNotFound = True
                break
    if nextNotFound:
        break

# Close the driver and store any remaining images and genres
driver.close()
np_mat = numpy.empty((0, 9075))
for img_url in img_urls:
    image = Image.open(requests.get(img_url, stream=True).raw)
    image = image.resize((55, 55))
    np_img = numpy.array(image)
    np_img = np_img.flatten()
    np_mat = numpy.append(np_mat, np_img[numpy.newaxis, :], axis=0)
np_mat = numpy.round(np_mat).astype(int)
pd.DataFrame(numpy.array(genres)).to_csv("~/Genre-Predictor/genres"+str(csvCount)+".csv")
numpy.savetxt("covers"+str(csvCount)+".csv", np_mat, delimiter=",")






