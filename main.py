import os.path
import pandas as pd
import csv

import smtplib  # Import smtplib for the actual sending function
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Import the email modules we'll need
from Agencies import getNewResults
from Agencies import saveNewResults

fromEmail = 'cmusso5@hotmail.com'
toEmail = "cmusso6@gmail.com; yuyamashita.y@gmail.com"
immoCSV = "/Users/cmusso/PycharmProjects/ImmoScrap/ImmoResults.csv"

boolSendEmail = True
agencies = ["Apleona", "Privera", "Wincasa","Livit", "HB", "EngelVoeklers"]


def sendEmail(txt):
    f = open("/Users/cmusso/PycharmProjects/ImmoScrap/config.txt", "r")
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



################################################################
if __name__ == '__main__':
    print(os.getcwd())

    if not os.path.isfile(immoCSV):
        with open(immoCSV, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            row = ["source", "id", "link", "rooms", "surface", "rent", "kreis", "floor", "start_date"]
            writer.writerow(row)

    df = pd.read_csv(immoCSV)
    immoIDs = df["id"].values

    immoRes = []
    for ag in agencies:
        agRes = getNewResults(ag, immoIDs)
        immoRes.append(agRes)
    immoFlat = [item for sublist in immoRes for item in sublist]

    saveNewResults(immoFlat, immoCSV)

    # If Results, Send Email
    if immoFlat and boolSendEmail:
        emailTxt = "Hi there! \nHere are your results: "
        for im in immoFlat:
            emailTxt = emailTxt + "\n" + str(im)
        sendEmail(str(emailTxt))
    else:
        print("NO email sent")
