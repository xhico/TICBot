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

## sudo apt-get install python python-pip python-setuptools python-lxml -y
## sudo python -m pip install --upgrade pip
## sudo pip install --no-cache-dir requests beautifulsoup4 python_dateutil lxml

import os
import time
import requests
import random
import csv
import glob
import datetime
import dateutil.parser
import smtplib
from xml.dom import minidom
from bs4 import BeautifulSoup
from multiprocessing import Process
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage



def send_mail(text, mail):
	fromaddr = "edersemelhante@gmail.com"
	toaddr = mail
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ", ".join(mail) 
	msg['Subject'] = text[0]
	
	body = text[1]
	msg.attach(MIMEText(body + "<br><br><p>- - - - - - - -<br>Para deixar de receber estes emails, entre \
						em contacto comigo:<br>https://www.facebook.com/Franc4Life</p>", 'html'))
	
	fp = open('eder.jpg', 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()
	msgImage.add_header('Content-ID', '<image1>')
	msg.attach(msgImage)
	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "Edersemelhante1")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	
	
def cleaner(curso):
	for filename in glob.glob(str(curso) + ".*"):
		if filename != str(curso) + ".txt":
			os.remove(filename)
		

def csv_reader(curso, file):
	mailList = list()
	
	with open(file, 'rb') as f:
		reader = csv.reader(f)
		allMails = list(reader)
	
	for entry in allMails:
		if entry[2] == curso:
			mailList.append(entry[1])
			
	return mailList


def getProxy():
	proxies = list()
	res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
	soup = BeautifulSoup(res.text,"lxml")
	for items in soup.select("tbody tr"):
		proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
		proxies.append(proxy_list)
		
	return random.choice(proxies)
	
	
def getFile(url, file, proxy):
	if os.path.exists(file):
		os.remove(file)
				
	counter = 0
	proxy_dict = {}
	while ((os.path.exists(file)) == False) and (counter < 5):
		try:
			if proxy:
				proxy_dict = {"http": getProxy()}
			r = requests.get(url, proxies = proxy_dict, timeout=5)

			with open(file, 'wb') as f:  
				f.write(r.content)
			f.close()
			
			# Verifica o conteudo
			with open(file) as f:  
				line = f.readline()
			f.close()
				
		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
			os.path.exists(file) == False
			counter += 1
			
	
def check_rss(curso):

	# Opens log file to get the last date
	with open("archive/" + curso + ".txt", 'r') as log:
		pubTime = log.readline()
	log.close()
	
	# Open xml file
	try:
		doc = minidom.parse(curso + ".xml")
	except:
		return None
		
	# Get all the items
	items = doc.getElementsByTagName("item")
	
	# Iterates on every item and compares the date with the First date
	for idx, item in enumerate(items):
		date = doc.getElementsByTagName("pubDate")[idx]
		tmpPubTime = str(datetime.datetime.strptime(date.firstChild.data, "%a, %d %b %Y %H:%M:%S %Z"))
		
		# If current date is more recent them First date
		# The current date becames the most recent date
		# Gets the 
		if tmpPubTime > pubTime:
			pubTime = tmpPubTime
			title = doc.getElementsByTagName("title")[idx+2]
			description = doc.getElementsByTagName("description")[idx+1]
			
			# Creates content list and enconde the content to UTF-8
			content = list()
			content.append(title.firstChild.data.encode('utf-8'))
			content.append(description.firstChild.data.encode('utf-8'))
			
			
			# Opens log file to store the most recent date and text
			with open("archive/" + curso + ".txt", "r") as log:
				old = log.read()
			log.close()
			
			with open("archive/" + curso + ".txt", "w") as log:
				log.write(pubTime)
				log.write("\n" + content[0])
				log.write("\n" + content[1])
				log.write("\n-----------------------\n")
				log.write(old)
			log.close()
			
	
			return content
		
		else:
			return None


def runner(curso, mailFile):
	print "START", curso
	feedFile = curso + ".xml"
	feedUrl = "http://side.utad.pt/rss.pl?" + curso

	cleaner(curso)
	getFile(feedUrl, feedFile, True)
	news = check_rss(curso)
	if news:
		print "new"
		#send_mail(news, csv_reader(curso, mailFile))
	cleaner(curso)
	print "FINISH", curso

if __name__ == '__main__':

	# TESTES
	#cursos = ["TIC", "EINF", "CMU", "EME", "ECN", "GES", "LRE", "PSI"]
	#mailUrl = "https://docs.google.com/spreadsheets/u/0/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv"
	
	# REAL SHIT
	#cursos = ["TIC", "EINF", "CMU", "EME", "ECN", "GES", "LRE", "PSI"]
	#mailUrl = "https://docs.google.com/spreadsheets/u/0/d/1HUFRioP96WZCZWaTR3bfTQeOg472dQyyGXrPzE4Nl3M/export?format=csv"
	
	mailFile = "mails.csv"
	
	while True:
		print "------------------------------"
		Pros = []
		getFile(mailUrl, mailFile, False)
		for curso in cursos:
			p = Process(target=runner, args=(curso,mailFile,))
			Pros.append(p)
			p.start()
			#runner(curso, mailFile)
		
		for t in Pros:
			t.join()
	
	
