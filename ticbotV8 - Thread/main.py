# -*- coding: utf-8 -*-
# !/usr/bin/env python3

##############################################
##  TICBot                                  ##
##                                          ##
##  @Autor: Francisco 'xhicoBala' Filipe    ##
##                                          ##
##  @Props: Filipe 'Nemo' Costa             ##
##                                          ##
##  SIDE Updater -- RSS Feed                ##
##                                          ##
##  Created:        2018/05/12              ##
##  Last Updated:   2020/10/12              ##
##############################################

# sudo apt-get install python3 python3-pip -y
# pip install --upgrade pip
# pip install -r requirements.txt --no-cache-dir

from os import system
from sys import platform
from time import sleep
from supFunctions import *
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def main(curso, mailList):
    """
    This is the main function for each course.
    :param: curso is string corresponding to each course
    :param: mailList is an array of the emails for that particular course
    :return: None
    """
    
    # Returns an array with the newest news
    news = checkInfo(curso)

    # Only if the array has something
    if news:
        # Writes to a log file (archive/[course].txt)
        writeLog(curso, news)
        # Sends the info to the students
        sendMail(curso, news, mailList)
        
    return None



if __name__ == '__main__':
    while True:
        mailURL = ""

        # archive/ and feeds/ HAVE TO EXIST in the root folder

        # Downloads the info from the GForm, returns a dictionary (key: course, value: array of emails)
        csvInfo = csvReader(mailURL)
        lstCursos = csvInfo.keys()

        # Uses multithreading to download all the rss feeds
        # Trying to get to the lowest time possible
        with ThreadPoolExecutor(max_workers=len(lstCursos)) as executor:
            executor.map(getRSS, lstCursos)

        # Foreach course runs the main function
        for curso, mailList in csvInfo.items():
            main(curso, mailList)











