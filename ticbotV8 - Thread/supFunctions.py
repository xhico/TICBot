# -*- coding: utf-8 -*-
# !/usr/bin/env python3


import csv
import requests
import feedparser
import datetime
import yagmail
import smtplib
import urllib3
from sys import maxsize
from os import path, remove
from proxy_requests import ProxyRequests
from random import randint

# File to manage the numbers of emails sent by each account.
accountsFile = "accounts.csv"

# Prints or no Prints
debug = True


def csvReader(mailURL):
    """
    Downloads csv with all the emails
    Reads the file and stores the information into a dictionary where
        Key = curso
        Value = list with all the emails regarding the curso
    :param: mailURL is a string pointing to the URL (GForm)
    :return: csvDict is a dictionary
    """
    
    if debug: print("csvReader")

    mailFile = "mails.csv"
    if path.exists(mailFile): remove(mailFile)
    with open(mailFile, 'wb') as fp:
        fp.write(requests.get(mailURL).content)
    fp.close()

    csvDict = dict()
    with open(mailFile, 'r') as fp:
        reader = csv.reader(fp)
        next(reader)
        for row in reader:
            if row[2] not in csvDict:
                csvDict[row[2]] = [row[1]]
            else:
                csvDict[row[2]].append(row[1])
    fp.close()

    return csvDict


def getRSS(curso):
    """
    Downloads xml rss files from https://side.utad.pt
    Stores them into feeds/curso.xml
    :param curso: string
    :return: True
    """
   
    if debug: print("getRSS", curso)

    
    feedRSS = "https://side.utad.pt/rss.pl?" + curso
    feedFile = "feeds/" + curso + ".xml"
    
    if path.exists(feedFile): remove(feedFile)

    try:
        r = ProxyRequests(feedRSS)
        r.get()
        with open(feedFile, 'wb') as f: f.write(r.get_raw())
        if round(path.getsize(feedFile)) < 700:
            getRSS(curso)

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ProxyError, urllib3.exceptions.MaxRetryError):
        getRSS(curso)


def checkInfo(curso):
    """
    Checks the curso xml file for the newest information
    Compares the dates from all the entries from the server with the latest date stored locally
    Stores the newsest entries inside a list
    :param curso: string
    :return entries: list sorted by date oldest to newest
    """
    
    if debug: print("checkInfo", curso)

    logFile = "archive/" + curso + ".txt"
    feedFile = "feeds/" + curso + ".xml"

    if path.exists(logFile):
        with open(logFile, 'r') as fp:
            lastPublished = fp.readline()
        fp.close()
    else:
        with open(logFile, 'w') as fp:
            lastPublished = "0000-00-00 00:00:00"
            fp.write(lastPublished)
        fp.close()

    newestNews = list()
    for entry in feedparser.parse(feedFile).entries:
        entryPubDate = str(datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z"))
        if entryPubDate > lastPublished:
            newestNews.append([entryPubDate, entry.title, entry.description])

    newestNews.sort(key=lambda entry: datetime.datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S"))

    if len(newestNews) == 0: return None
    return newestNews


def writeLog(curso, newestNews):
    """
    Writes every entry to the log file, oldest to newest
    :param newestNews: list where each element is a list containing an entry
    :param curso: string
    :return: True
    """

    if debug: print("writeLog", curso)

    logFile = "archive/" + curso + ".txt"

    for entry in newestNews:
        with open(logFile, 'r') as fp:
            oldInfo = fp.read()
        fp.close()
        with open(logFile, 'w') as fp:
            fp.write(entry[0] + "\n" + entry[1] + "\n" + entry[2] + "\n-----------------------\n")
            fp.write(oldInfo)
        fp.close()

    return True


def resetAccounts():
    """
    Reset the accounts.csv.
    Writes the counter for all the accounts to 0 emails sent
    :return: True
    """
    
    if debug: print("resetAccounts")

    if path.exists(accountsFile): remove(accountsFile)
    with open(accountsFile, 'w') as fp:
        fp.write("name,sent\n")
        for i in [x for j, x in enumerate(range(18)) if j != 4]:
            if i == 0:
                fp.write("edersemelhante@gmail.com,")
            else:
                fp.write("edersemelhante" + str(i) + "@gmail.com,")
            fp.write("0\n")
    fp.close()

    return True


def getEmail():
    """
    Reads the emails.csv to get the email account index with the least number of emails sent
    :return: idx is an int containing the index of the email
    """

    if debug: print("getEmail")

    if not path.exists(accountsFile): resetAccounts()

    with open(accountsFile, 'r') as fp:
        accountsInfo = [x for x in csv.reader(fp, delimiter=',')]
        del accountsInfo[0]
    fp.close()
    return accountsInfo[[int(x[1]) for x in accountsInfo].index(min([int(x[1]) for x in accountsInfo]))][0]


def setEmailSent(accName, numb):
    """
    Updated de accounts.csv with the newest info regarding the
    number of emails sent from an account
    :param accName: string
    :param numb: int
    :return: True
    """
    
    if debug: print("setEmailSent", accName)

    with open(accountsFile, 'r') as fp:
        accountsInfo = [x for x in csv.reader(fp, delimiter=',')]
    fp.close()

    for row in accountsInfo:
        if accName == row[0]:
            if int(row[1]) == maxsize:
                row[1] = str(numb)
            else:
                row[1] = str(int(row[1]) + numb)

    remove(accountsFile)
    with open(accountsFile, 'w') as fp:
        for row in accountsInfo:
            fp.write(row[0] + "," + row[1] + '\n')
    fp.close()

    return True


def sendMail(curso, newestNews, mailList):
    """
    Send each entry from newestNews to the designated emails
    Send each email by calling getEmail() to get witch email account to send from
    :param curso: string
    :param newestNews: list where each element is a list containing an entry
    :param mailList: list where each element is a string containing one email
    :return: True
    """
    
    if debug: print("sendMail", curso)

    for entry in newestNews:
    
        # Splits the mailList, trying to avoid bot detection!
        tmpNumb = randint(15, 20)
        for mailList in [mailList[x:x + tmpNumb] for x in range(0, len(mailList), tmpNumb)]:

            sender_email = getEmail()

            yag = yagmail.SMTP(sender_email, "password")
            body = entry[2], \
                   "<b><br><br>- - - - - - - -<br>Aviso publicado às: " + entry[0] + "</b>", \
                   "<b>- - - - - - - -<br>Partilhem: https://goo.gl/forms/5Ot2CkOYzMmG4ONf1</b>", \
                   "<b>- - - - - - - -<br>Não vale a pena responder a este mail..! É um bot..!<br>Para deixar de receber estes emails, entre em contacto comigo:<br>https://www.facebook.com/Franc4Life</b>"

            try:
                yag.send(mailList, curso + " - " + entry[1], body)
                setEmailSent(sender_email, len(mailList))
            except smtplib.SMTPDataError:
                setEmailSent(sender_email, maxsize)
            yag.close()

    return True
