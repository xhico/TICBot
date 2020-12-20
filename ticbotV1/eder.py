#-*- coding: utf-8 -*-
#!/usr/bin/env python2

##############################################
##				  TICBot		  			##
##											##
##   @Autor: Francisco 'xhicoBala' Filipe	##
##											##
##	 @Props	 Filipe 'Nemo' Costa			##
##			 Gringo de LEI que tebe a ideia ##
##											##
##	 SIDE Updater -- RSS Feed				##
##	 2018/05/12 01:09 AM					##
##############################################

## Close all python scripts
## sudo apt-get install python-pip -y && sudo apt-get install python-setuptools -y && sudo pip install requests && sudo python -m pip install --upgrade pip
## sudo pip install python-dateutil feedparser
## cls && xcopy /Y old.txt tic.txt && xcopy /Y old.txt lei.txt && python eder.py
## clear && cd && cd ticbot/ && rm -rf tic.txt lei.txt && cp old.txt tic.txt && cp old.txt lei.txt && python eder.py && cd

import os
import time
import feedparser
import smtplib
import datetime
import dateutil.parser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from random import randint
import requests
import csv


		
		
def send_mail(text, mail):

	fromaddr = "edersemelhante@gmail.com"
	toaddr = mail
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ", ".join(mail) 
	msg['Subject'] = text[0] 

	body = text[1]
	msg.attach(MIMEText(body, 'html'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "Edersemelhante1")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()

def rss(feed):
	
	if feed == "tic":
		file = "tic.txt"
		feed = "http://side.utad.pt/rss.pl?TIC"
	if feed == "lei":
		file ="lei.txt"
		feed = "http://side.utad.pt/rss.pl?EINF"
	
	d = feedparser.parse(feed)

	f = open(file, "r") 
	recPubTime = f.readline()
	f.close
	
	dateList = list()
	
	numbTry = 1
	tempo = 1
	while numbTry != 7:
		for entry in d["entries"]:
			pubTime = str(datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z"))
			dateList.append(pubTime)
		dateList = sorted(dateList, key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
					
		#print "try",numbTry,feed, tempo
		time.sleep(tempo)
		tempo=tempo*2
		numbTry += 1
		
		if len(dateList) != 0:
			break

	if numbTry == 7:
		return None
	
	if recPubTime != dateList[-1]:

		f = open(file, "w")
		f.write(dateList[-1])
		f.close
		
		for i in range(0, len(d["entries"]), 1):
			if str(datetime.datetime.strptime(d["entries"][i].published, "%a, %d %b %Y %H:%M:%S %Z")) == dateList[-1]:
				title = d["entries"][i].title
				description = d["entries"][i].description
				
				content = list()
				content.append(title.encode('utf-8'))
				content.append(description.encode('utf-8'))
				return content
	else:
		return None

def downloader(file, url):
	if os.path.exists(file):
		os.remove(file)
		
	r = requests.get(url)
	with open(file, 'wb') as f:  
		f.write(r.content)

def csv_reader(file):
	with open(file, 'rb') as f:
		reader = csv.reader(f)
		full_list = list(reader)
	
	tic_mail_list = list()
	lei_mail_list = list()
	
	for entry in full_list:
		if entry[2] == "TIC":
			tic_mail_list.append(entry[1])
		if entry[2] == "LEI":
			lei_mail_list.append(entry[1])
			
	return tic_mail_list, lei_mail_list



while True:
	file = "ticbot.csv"
	url = "https://docs.google.com/spreadsheets/u/0/d/1HUFRioP96WZCZWaTR3bfTQeOg472dQyyGXrPzE4Nl3M/export?format=csv"
	
	#file = "teste.csv"
	#url = "https://docs.google.com/spreadsheets/u/1/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv"
	
	
	content_tic = rss("tic")
	if content_tic:
		#print content_tic
		downloader(file, url)
		tic_mail_list = csv_reader(file)[0]
		send_mail(content_tic, tic_mail_list)

	#print "\n"
	
	content_lei = rss("lei")
	if content_lei:
		#print content_lei
		downloader(file, url)
		lei_mail_list = csv_reader(file)[1]
		send_mail(content_lei, lei_mail_list)

	#print "again"



