# -*- coding: utf-8 -*-
# !/usr/bin/env python3

##############################################
##  TICBot                                  ##
##                                          ##
##  @Autor: Francisco 'xhicoBala' Filipe    ##
##                                          ##
##  @Props: Filipe 'Nemo' Costa             ##
##          Gringo de LEI que tebe a ideia  ##
##                                          ##
##  SIDE Updater -- RSS Feed                ##
##                                          ##
##  Created: 2018/05/12 01:09 AM            ##
##  Updated: 2020/01/27 00:56 AM            ##
##############################################

# sudo apt install python3 python3-pip -y
# sudo python3 -m pip install --upgrade pip
# sudo python3 -m pip install --no-cache-dir requests feedparser proxy_requests

import os
import csv
import requests
import feedparser
import datetime
import smtplib
from sys import platform
from proxy_requests import ProxyRequests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def getRSS(curso):
    if debug: print("getRSS")

    # VARS
    feedRSS = "https://side.utad.pt/rss.pl?" + curso
    feedFile = "feeds/" + curso + ".xml"

    try:
        # DOWNLOAD DA INFO -> PROXY
        r = ProxyRequests(feedRSS)
        r.get()

        # ESCREVE A INFO
        if os.path.exists(feedFile): os.remove(feedFile)

        with open(feedFile, 'wb') as f:
            f.write(r.get_raw())
    except:
        if debug: print("Proxy Error")
        pass


def checkInfo(curso):
    if debug: print("checkInfo")

    # LISTA COM AS ENTRIES NOVAS
    newEntries = list()

    # GUARDA A ULTIMA DATA ENVIADA
    with open("archive/" + curso + ".txt", 'r') as log:
        lastPublished = log.readline()
    log.close()

    # PARA CADA ENTRY VERIFICA SE A DATA É MAIS RECENTE
    # DO QUE A ULTIMA ENTRY ENVIADA
    # GUARDA NA LISTA newEntries
    info = feedparser.parse("feeds/" + curso + ".xml")

    entries = info.entries
    if len(entries) != 0:

        for entry in entries:
            entryPublished = str(datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z"))

            # if debug: print (entryPublished, lastPublished)

            if entryPublished > lastPublished:
                entryList = list()
                entryList.append(entryPublished)
                entryList.append(entry.title)
                entryList.append(entry.description)
                newEntries.append(entryList)

        # SE A newEntries ESTIVER PREENCHIDA RETORNA
        if len(newEntries) != 0:
            return newEntries
        else:
            return None

    else:
        return None


def writeLog(curso, news):
    if debug: print("writeLog")

    # VARS
    logFile = "archive/" + curso + ".txt"

    for entry in news:
        # GUARDA A INFO JÁ PRESENTE
        with open(logFile, 'r') as log:
            old = log.read()
        log.close()

        # ESCREVE A INFO RECENTE
        # ESCREVE A INFO ANTIGA
        with open(logFile, 'w') as log:
            log.write(entry[0])
            log.write("\n" + entry[1])
            log.write("\n" + entry[2])
            log.write("\n-----------------------\n")
            log.write(old)
        log.close()


def sendMail(curso, news, mailList):
    if debug: print("sendMail")

    n = round(len(mailList) / 2) + 1
    lst = [mailList[x:x + n] for x in range(0, len(mailList), n)]

    for i, mailList in enumerate(lst):

        if i == 0:
            fromaddr = "edersemelhante@gmail.com"
            passw = "Edersemelhante1"
        else:
            fromaddr = "edersemelhante1@gmail.com"
            passw = "Edersemelhante2."

        for entry in news:
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = ", ".join(mailList)
            msg['Subject'] = curso + " - " + entry[1]

            msg.attach(MIMEText(entry[
                                    2] + "<br><br><p>- - - - - - - -<br>Para deixar de receber estes emails, entre em contacto comigo:<br>https://www.facebook.com/Franc4Life</p>",
                                'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, passw)
            text = msg.as_string()
            server.sendmail(fromaddr, mailList, text)
            server.quit()


def csvReader(file):
    if debug: print("csvReader")

    with open(file, 'r') as fp:
        reader = csv.reader(fp)
        infos = list(reader)
    fp.close()
    infos.remove(infos[0])

    csvDict = dict()
    for line in infos:
        if (line[2]) in csvDict:
            csvDict[line[2]].append(line[1])
        else:
            csvDict[line[2]] = [line[1]]
    return csvDict


def main(curso, mailList):
    if debug: print("main - " + curso + " - " + str(mailList))

    if not os.path.exists("archive/" + curso + ".txt"):
        with open("archive/" + curso + ".txt", 'w') as fp:
            fp.write("0000-00-00 00:00:00")
        fp.close()

    getRSS(curso)
    news = checkInfo(curso)

    if news is not None:
        news = news[::-1]

        # ORDENA A LISTA POR DATA
        news.sort(key=lambda entry: datetime.datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S"))

        sendMail(curso, news, mailList)
        writeLog(curso, news)


debug = True
if __name__ == '__main__':

    while True:
        if platform == "linux" or platform == "linux2":
            if debug: os.system("clear")
        elif platform == "win32":
            if debug: os.system("cls")

        # TESTES
        mailUrl = 'https://docs.google.com/spreadsheets/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv'

        # FOR REAL
        # mailUrl = 'https://docs.google.com/spreadsheets/d/1HUFRioP96WZCZWaTR3bfTQeOg472dQyyGXrPzE4Nl3M/export?format=csv'

        # DOWNLOAD MAIL CSV
        # GET mailCursosDic
        mailFile = "mails.csv"
        if os.path.exists(mailFile): os.remove(mailFile)
        try:
            with open(mailFile, 'wb') as fp:
                fp.write(requests.get(mailUrl).content)
        except:
            if debug: print("CSV Cant Download")
            pass
        mailCursosDict = csvReader(mailFile)

        # RUN MAIN FOR VALID CURSOS
        for curso, mailList in mailCursosDict.items():
            main(curso, mailList)
