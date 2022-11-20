from bs4 import BeautifulSoup as bs
import requests
from Immo import Immo
from urllib.parse import urljoin

agencyURLDict = {
    "Livit": 'https://www.livit.ch/fr/search/residental?category=APPT&location=Z%C3%BCrich%2C%20Switzerland&geo[value]=47.3768866%2C8.541694&geo[distance][from]=0&price[min]=2700&price[max]=3500&rooms[min]=3.5&surface_living[min]=70',
    "HB": "https://www.hbre.ch/de/suche?offer_type=RENT&offer_category=APPT&location=Z%C3%BCrich&search=",
"EngelVoeklers": "https://www.engelvoelkers.com/fr/search/?q=&startIndex=0&businessArea=residential&sortOrder=DESC&sortField=sortPrice&pageSize=18&facets=bsnssr%3Aresidential%3Bcntry%3Aswitzerland%3Brgn%3Azurich%3Btyp%3Arent%3Brms%3A%5B3.0+TO+5.5%5D%3B"
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
    elif agency == "EngelVoeklers":
        print("Processing EngelVoeklers...")
        return getEngelVoeklersResults(soup, url, immoIDs)
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
