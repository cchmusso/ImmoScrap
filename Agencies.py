from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


import time
import re

import requests
from Immo import Immo
from urllib.parse import urljoin

CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'

agencyURLDict = {
    "Livit": 'https://www.livit.ch/fr/search/residental?category=APPT&location=Z%C3%BCrich%2C%20Switzerland&geo[value]=47.3768866%2C8.541694&geo[distance][from]=0&price[min]=2700&price[max]=3500&rooms[min]=3.5&surface_living[min]=70',
    "Apleona": "https://realestate-ch.apleona.com/angebot/mietangebote/",
    "Privera": "https://www.privera.ch/fr/offre-de-biens-immobiliers/annonces",
    "Wincasa": 'https://www.wincasa.ch/fr-ch/locataires-potentiel/logements',
    "HB": "https://www.hbre.ch/de/suche?offer_type=RENT&offer_category=APPT&location=Z%C3%BCrich&search=",
    "EngelVoeklers": "https://www.engelvoelkers.com/fr/search/?q=&startIndex=0&businessArea=residential&sortOrder=DESC&sortField=sortPrice&pageSize=18&facets=bsnssr%3Aresidential%3Bcntry%3Aswitzerland%3Brgn%3Azurich%3Btyp%3Arent%3Brms%3A%5B3.0+TO+5.5%5D%3B",
    "Verit": "https://www.verit.ch/mieten-kaufen/mieten",
    "SBB": "https://sbb-immobilien.ch/fr/louer/",
    "Ledermann": "https://ledermann.com/de/mieten/verfuegbare-objekte/?category=APPT&search=&area=&price_from=2500&price_to=3500&rooms_from=3.5"
}

def saveNewResults(immoRes, immoCSV):
    for res in immoRes:
        res.writeCSV(immoCSV)

def getNewResults(agency, immoIDs):
    url = agencyURLDict[agency]
    req = requests.get(url)
    soup = bs(req.text, "html.parser")

    if agency == "Livit":
        print("Processing Livit...")
        return getLivitResults(soup, url, immoIDs)
    elif agency == "Apleona":
        print("Processing Apleona...")
        return getApleonaResults(soup, url, immoIDs)
    elif agency == "Privera":
        print("Processing Privera...")
        return getPriveraResults(soup, url, immoIDs)
    elif agency == "Wincasa":
        print("Processing Wincasa...")
        return getWincasaResults(soup, url, immoIDs)
    elif agency == "HB":
        print("Processing HB...")
        return getHBResults(soup, url, immoIDs)
    elif agency == "EngelVoeklers":
        print("Processing EngelVoeklers...")
        return getEngelVoeklersResults(soup, url, immoIDs)
    elif agency == "Ledermann":
        print("Processing Ledermann...")
        return getLedermannResults(soup, url, immoIDs)
    elif agency == "Verit":
        print("Processing Verit...")
        return getVeritResults(soup, url, immoIDs)
    elif agency == "SBB":
        print("Processing SBB...")
        return getSBBResults(soup, url, immoIDs)
    else:
        return


def getDriver():
    options = Options()
    # options.headless = True
    options.add_argument("--window-size=1920,1200")

    desired_capabilities = DesiredCapabilities.CHROME.copy()
    desired_capabilities['acceptInsecureCerts'] = True

    return webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH,
                            desired_capabilities=desired_capabilities)
def getSBBResults(soup, url, immoIDs):
    driver = getDriver()
    driver.get(url)
    time.sleep(1)

    cookie = driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
    if cookie:
        cookie.click()

    time.sleep(1)

    driver.find_element(By.XPATH, "//input[@id='casawpUtilityLiving']/ancestor::label").click()

    driver.find_element(By.XPATH, "//label[contains(text(),'Pièces')]/following-sibling::span").click()
    driver.find_element(By.XPATH, "//input[@id='casawpRoomsFrom']").send_keys("3.5")
    driver.find_element(By.XPATH, "//input[@id='casawpRoomsFrom']").send_keys(Keys.ENTER)
    time.sleep(1)

    driver.find_element(By.XPATH, "//label[contains(text(),'Prix')]/following-sibling::span").click()
    driver.find_element(By.XPATH, "//input[@id='casawpPriceFrom']").send_keys("2500")
    driver.find_element(By.XPATH, "//input[@id='casawpPriceFrom']").send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@id='casawpPriceTo']").send_keys("3500")
    driver.find_element(By.XPATH, "//input[@id='casawpPriceTo']").send_keys(Keys.ENTER)
    time.sleep(1)

    driver.find_element(By.CLASS_NAME, "mapboxgl-ctrl-geocoder--input").send_keys("Zürich, Kanton Zürich, Schweiz")
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, "mapboxgl-ctrl-geocoder--input").send_keys(Keys.ENTER)
    time.sleep(2)

    #submit
    driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn--with-icon']").click()
    time.sleep(1)
    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("div", {"class": "casawp-property"}):
        href = res.find("a").get('href')
        link = href
        id = re.search('.*/(.*)fr.*/$', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find("div", {"class": "casawp-property__text__data"}).findChildren("div", recursive=False)
        rooms = info[2].text.strip()
        surface = info[1].text.strip()
        rent = info[0].text.strip()
        kreis = re.search('.*,(.*)$', info[3].text.strip()).group(1)
        floor = ""
        start_date = ""

        im = Immo("SBB", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes

def getVeritResults(soup, url, immoIDs):

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
    driver.get(url)
    time.sleep(1)

    cookie = driver.find_element(By.XPATH, "//div[@id='popup-buttons']/button")
    if cookie:
        cookie.click()

    time.sleep(1)
    driver.switch_to.frame(0)

    #Location
    driver.find_element(By.CLASS_NAME, "mapboxgl-ctrl-geocoder--input").send_keys("Zürich, Kanton Zürich, Schweiz")
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, "mapboxgl-ctrl-geocoder--input").send_keys(Keys.ENTER)

    driver.find_element(By.XPATH, "//span[contains(text(),'Zimmer')]/ancestor::button").click()
    driver.find_element(By.XPATH, "//div[@class='dropdown-menu']/button[@value='3']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//span[contains(text(),'Preis')]/ancestor::button").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//div[@class='dropdown-menu']/button[@value='2750']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//div[@class='dropdown-menu']/button[@value='3500']").click()
    time.sleep(1)

    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("div", {"class": "listing-thumb embedded"}):
        href = res.find("a").get('href')
        link = "https://flatfox.ch/" + href
        id = re.search('.*/(.*)/$', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue

        rooms = res.find("h2").find(text=True, recursive=False)
        surface = ""
        rent = res.find("span", {"class": "price"}).text.strip()
        kreis = res.find("span", {"class": "listing-thumb-title__location"}).text.strip()
        floor = ""
        start_date = ""

        im = Immo("Verit", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes

def getApleonaResults(soup, url, immoIDs):

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
    driver.get(url)
    time.sleep(1)

    cookie = driver.find_element(By.XPATH, "//div[@class='cc-compliance']/a")
    if cookie:
        cookie.click()

    time.sleep(1)
    driver.switch_to.frame(0)

    location = driver.find_element(By.ID, "zipCityText").send_keys("Zürich")
    time.sleep(1)
    location = driver.find_element(By.ID, "zipCityText").send_keys(Keys.ENTER)

    time.sleep(1)
    rent_min = Select(driver.find_element(By.XPATH, "//div[@id='PriceFromSelect']/select")).select_by_value('26h')
    time.sleep(1)
    rent_max = Select(driver.find_element(By.XPATH, "//div[@id='PriceToSelect']/select")).select_by_value('35h')
    time.sleep(1)
    rooms = Select(driver.find_element(By.XPATH, "//div[@id='SizePrimaryFromSelect']/select")).select_by_value('3')
    time.sleep(1)
    surface = Select(driver.find_element(By.XPATH, "//div[@id='SizeSecondaryFromSelect']/select")).select_by_value('80')
    time.sleep(1)

    submit = driver.find_element(By.XPATH, "//a[@id='btnShowResultTop']").click()
    time.sleep(1)

    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("li", {"class": "object-list-item"}):
        href = res.find("a").get('href')
        link = "https://1003.hci-is24.ch/" + href
        id = re.search('p=(.*)&se=', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find("div", {"class": "object-details"}).findChildren("div", recursive=False)
        rooms = info[0].text.splitlines()[2].strip()
        surface = info[2].text.splitlines()[0].strip()
        rent = res.find("span", {"class": "price"}).text.strip()
        kreis = res.find("div", {"class": "object-address"}).text.splitlines()[3].strip()
        floor = ""
        start_date = res.find("div", {"class": "object-availability"}).text.strip()

        im = Immo("Apleona", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes
def getPriveraResults(soup, url, immoIDs):

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
    driver.get(url)

    time.sleep(1)
    driver.switch_to.frame(0)

    location =  Select(driver.find_element(By.XPATH, "//div[@id='CitiesSelect']/select")).select_by_visible_text('Zürich')
    time.sleep(1)
    rent_min = Select(driver.find_element(By.XPATH, "//div[@id='PriceFromSelect']/select")).select_by_value('26h')
    time.sleep(1)
    rent_max = Select(driver.find_element(By.XPATH, "//div[@id='PriceToSelect']/select")).select_by_value('35h')
    time.sleep(1)
    rooms = Select(driver.find_element(By.XPATH, "//div[@id='SizePrimaryFromSelect']/select")).select_by_value('3')
    time.sleep(1)
    surface = Select(driver.find_element(By.XPATH, "//div[@id='SizeSecondaryFromSelect']/select")).select_by_value('80')
    time.sleep(1)

    submit = driver.find_element(By.XPATH, "//a[@id='btnShowResultTop']").click()
    time.sleep(1)

    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("li", {"class": "object-list-item"}):
        href = res.find("a").get('href')
        link = "https://743.hci-is24.ch/" + href
        id = re.search('p=(.*)&se=', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find("div", {"class": "object-details"}).findChildren("div", recursive=False)
        rooms = info[0].text.splitlines()[2].strip()
        surface = info[2].text.splitlines()[0].strip()
        rent = res.find("span", {"class": "price"}).text.strip()
        kreis = res.find("div", {"class": "object-address"}).text.splitlines()[3].strip()
        floor = ""
        start_date = res.find("div", {"class": "object-availability"}).text.strip()

        im = Immo("Privera", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes

def getLedermannResults(soup, url, immoIDs):

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
    driver.get(url)

    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("div", {"class": "offer-item"}):
        href = res.find("a").get('href')
        link = href
        id = re.search('.*/(.*)/$', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find("div", {"class": "row"}).find("div", {"class": "row"}).findChildren("div", recursive=False)
        rooms = info[2].text.strip().splitlines()[0].strip()
        surface = info[2].text.strip().splitlines()[2].strip()
        rent = res.find("span", {"class": "currency"}).text.strip()
        kreis = info[1].text.splitlines()[1].strip()
        floor = info[2].text.splitlines()[1].strip()
        start_date = ""

        im = Immo("Ledermann", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes
def getWincasaResults(soup, url, immoIDs):

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
    driver.get(url)

    cookie = driver.find_element(By.XPATH, "//button[@id='acceptAllCookies']")
    if cookie:
        cookie.click()

    time.sleep(1)
    driver.switch_to.frame(0)

    location = driver.find_element(By.ID, "zipCityText").send_keys("Zürich")
    time.sleep(1)
    rent_min = Select(driver.find_element(By.XPATH, "//div[@id='PriceFromSelect']/select")).select_by_value('26h')
    time.sleep(1)
    rent_max = Select(driver.find_element(By.XPATH, "//div[@id='PriceToSelect']/select")).select_by_value('35h')
    time.sleep(1)
    rooms = Select(driver.find_element(By.XPATH, "//div[@id='SizePrimaryFromSelect']/select")).select_by_value('3')
    time.sleep(1)
    surface = Select(driver.find_element(By.XPATH, "//div[@id='SizeSecondaryFromSelect']/select")).select_by_value('80')
    time.sleep(1)

    submit = driver.find_element(By.XPATH, "//a[@id='btnShowResultTop']").click()
    time.sleep(1)

    soup = bs(driver.page_source, 'lxml')
    #print(driver.page_source)
    driver.quit()

    immoRes = []
    for res in soup.find_all("li", {"class": "object-list-item"}):
        href = res.find("a").get('href')
        link = "https://264.hci-is24.ch/" + href
        id = re.search('p=(.*)&se=', href).group(1)
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find("div", {"class": "object-details"}).findChildren("div", recursive=False)
        rooms = info[0].text.splitlines()[2].strip()
        surface = info[2].text.splitlines()[0].strip()
        rent = res.find("span", {"class": "price"}).text.strip()
        kreis = res.find("div", {"class": "object-address"}).text.splitlines()[3].strip()
        floor = ""
        start_date = res.find("div", {"class": "object-availability"}).text.strip()

        im = Immo("Wincasa", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
        #im.printDetails()
    return immoRes

def getLivitResults(soup, url, immoIDs):
    immoRes = []
    for res in soup.find_all("div", {"class": "flex flex-col"}):
        href = res.find("a").get('href')
        link = urljoin(url, href)
        id = href.rsplit('/', 1)[1]
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find_all("div", {"class": "text-sm font-neue font-light whitespace-nowrap"})
        rooms = info[0].text.strip()
        surface = info[1].text.strip()
        rent = info[2].text.strip()
        kreis = info[3].text.strip()
        floor = info[4].text.strip()
        start_date = info[5].text.strip()

        im = Immo("Livit", id, link, rooms, surface, rent, kreis, floor, start_date)
        immoRes.append(im)
        print(im)
    return immoRes

def getHBResults(soup, url, immoIDs):
    immoRes = []

    for res in soup.find_all("div", {"class": "offer darkgreen"}):
        href = res.find("a").get('href')
        link = urljoin(url, href)
        id = href.rsplit('--', 1)[1]
        if id in immoIDs:
            print("Skipping ID" + id)
            continue

        kreis = res.find("div", {"class": "fadeInTile"}).find("span").text
        info = str(res.find("p")).split("<br/>")
        rooms = float(info[1].rsplit(':', 1)[1].strip())
        if rooms < 3:
            continue
        surface = info[0].replace("<p>Fläche:","").strip()
        rent = info[2].replace("Bruttomiete:", "").strip()
        floor = ""
        start_date = ""

        im = Immo("HB", id, link, rooms, surface, rent, kreis, floor, start_date)
        print(im)
        immoRes.append(im)

    return immoRes

def getEngelVoeklersResults(soup, url, immoIDs):
    immoRes = []

    for res in soup.find_all("a", {"class": "ev-property-container"}):
        href = res.get('href')
        if not href:
            continue
        link = urljoin(url, href)
        id = href.rsplit('-', 1)[1]
        if id in immoIDs:
            print("Skipping ID" + id)
            continue

        rent = res.find("div", {"class": "ev-value"}).text.replace("CHF", "").replace(".", "")
        kreis = res.find("div", {"class": "ev-teaser-subtitle"}).text.rsplit(',', 1)[1].strip()
        info = res.find_all("div", {"class": "ev-teaser-attribute"})

        rooms = info[0].text.strip()
        surface = info[1].text.strip()
        floor = ""
        start_date = ""

        im = Immo("EngelVoekler", id, link, rooms, surface, rent, kreis, floor, start_date)
        print(im)
        immoRes.append(im)

    return immoRes
