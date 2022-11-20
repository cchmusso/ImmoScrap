from bs4 import BeautifulSoup as bs
import requests
import os.path
import pandas as pd
from immo import Immo

import smtplib  # Import smtplib for the actual sending function
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Import the email modules we'll need

from urllib.parse import urljoin

fromEmail = 'cmusso5@hotmail.com'
toEmail = "cmusso6@gmail.com"#, yuyamashita.y@gmail.com"
immoCSV = "./ImmoResults.csv"

immoDict = {
    "livit": 'https://www.livit.ch/fr/search/residental?category=APPT&location=Z%C3%BCrich%2C%20Switzerland&geo[value]=47.3768866%2C8.541694&geo[distance][from]=0&price[min]=2700&price[max]=3500&rooms[min]=3.5&surface_living[min]=70',
    "wincasa": "https://www.wincasa.ch/fr-ch/locataires-potentiel/logements"
}

def sendEmail(txt):
    f = open("config.txt", "r")
    # initialize the SMTP server
    server = smtplib.SMTP(host="smtp.office365.com", port=587)
    server.starttls() # connect to the SMTP server as TLS mode (secure) and send EHLO
    server.login(fromEmail, f.read()) # login to the account using the credentials

    # initialize the message we wanna send
    msg = MIMEMultipart("alternative")
    msg["From"] = "Clairouuu Coding <"+fromEmail+">"
    msg["To"] = toEmail
    msg["Subject"] = "New Immo Results"
    text_part = MIMEText(txt, "plain")
    msg.attach(text_part)

    # send the email
    server.sendmail(fromEmail, toEmail, msg.as_string())
    # terminate the SMTP session
    server.quit()

    print("Email sent :)")






def storeNewLivit(immoIDs):
    url = "https://www.livit.ch/fr/search/residental?category=APPT&location=Z%C3%BCrich%2C%20Switzerland&geo[value]=47.3768866%2C8.541694&geo[distance][from]=0&price[min]=2700&price[max]=3500&rooms[min]=3.5&surface_living[min]=70"
    req = requests.get(url)
    soup = bs(req.text, "html.parser")
    immoRes = []
    for res in soup.find_all("div", {"class": "flex flex-col"}):
        href = res.find("a").get('href')
        link = urljoin(url, href)
        id = href.rsplit('/', 1)[1]
        if immoIDs.str.contains(id).any():
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
        # im.print()
        im.writeCSV(immoCSV)
        immoRes.append(im)
    return immoRes


################################################################
if __name__ == '__main__':
    if not os.path.isfile(immoCSV):
        with open(immoCSV, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            row = ["source", "id", "link", "rooms", "surface", "rent", "kreis", "floor", "start_date"]
            writer.writerow(row)

    df = pd.read_csv(immoCSV)
    immoIDs = df["id"]

    immoRes = storeNewLivit(immoIDs)

    if immoRes:
        emailTxt = "Hi there! \nHere are your results: "
        for im in immoRes:
            emailTxt = emailTxt + "\n" + str(im)
        sendEmail(str(emailTxt))
    else:
        print("NO new results 😞")
