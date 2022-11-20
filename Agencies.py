from bs4 import BeautifulSoup as bs
import requests
from Immo import Immo
from urllib.parse import urljoin

agencyURLDict = {
    "Livit": 'https://www.livit.ch/fr/search/residental?category=APPT&location=Z%C3%BCrich%2C%20Switzerland&geo[value]=47.3768866%2C8.541694&geo[distance][from]=0&price[min]=2700&price[max]=3500&rooms[min]=3.5&surface_living[min]=70',
    "HB": "https://www.hbre.ch/de/suche?offer_type=RENT&offer_category=APPT&location=Z%C3%BCrich&search="
}


def getNewResults(agency, immoIDs):
    url = agencyURLDict[agency]
    req = requests.get(url)
    soup = bs(req.text, "html.parser")

    if agency == "Livit":
        print("Processing Livit...")
        return getLivitResults(soup, url, immoIDs)
    elif agency == "HB":
        print("Processing HB...")
        return getHBResults(soup, url, immoIDs)
    else:
        return


def saveNewResults(immoRes, immoCSV):
    for res in immoRes:
        res.writeCSV(immoCSV)


def getLivitResults(soup, url, immoIDs):
    immoRes = []
    for res in soup.find_all("div", {"class": "flex flex-col"}):
        href = res.find("a").get('href')
        link = urljoin(url, href)
        id = href.rsplit('/', 1)[1]
        if id in immoIDs:
            print("Skipping ID" + id)
            continue
        info = res.find_all("div", {"class": "text-sm font-neue font-light"})
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
        surface = info[0].strip()
        rent = info[2].strip()
        floor = ""
        start_date = ""

        im = Immo("HB", id, link, rooms, surface, rent, kreis, floor, start_date)
        print(im)
        immoRes.append(im)

    return immoRes
