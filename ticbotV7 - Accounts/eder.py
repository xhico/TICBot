# -*- coding: utf-8 -*-
# !/usr/bin/env python3

##############################################
##  TICBot                                  ##
##                                          ##
##  @Autor: Francisco 'xhicoBala' Filipe    ##
##                                          ##
##  @Props: Filipe 'Nemo' Costa             ##
##          Gringo de LEI que teve a ideia  ##
##                                          ##
##  SIDE Updater -- RSS Feed                ##
##                                          ##
##  Created: 2018/05/12 01:09 AM            ##
##############################################

# sudo apt install python3 python3-pip -y
# sudo python3 -m pip install --upgrade pip
# sudo python3 -m pip install --no-cache-dir requests feedparser proxy_requests yagmail

from os import system
from sys import platform
from semelhante import *


def main():
    debug = False

    if debug:
        if platform == "linux": system("clear")
        if platform == "win32": system("cls")

    # TESTES
    # mailURL = "https://docs.google.com/spreadsheets/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv"

    # FOR REAL
    mailURL = "https://docs.google.com/spreadsheets/d/1qhXJcsyHsgDPaTIE0gJdijqhfzQsC4Pc5qezSyoB7Y8/export?format=csv"

    for curso, mailList in csvReader(mailURL).items():
        if debug: print("----------------\n" + curso + "\ngetRSS")
        getRSS(curso)

        if debug: print("checkInfo")
        news = checkInfo(curso)

        if news:
            if debug: print("writeLog")
            writeLog(curso, news)

            if debug: print("sendMail")
            sendMail(curso, news, mailList)


if __name__ == '__main__':
    while True: main()
