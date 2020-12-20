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
## sudo pip install --no-cache-dir python_dateutil requests beautifulsoup4 lxml feedparser

import os
import csv
import time
import random
import smtplib
import datetime
import requests
import feedparser
from bs4 import BeautifulSoup
from multiprocessing import Process
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart


def getProxy():
	#print "Proxy..."
	
	# Cria uma lista com proxies
	proxies = list()
	
	counter = 0
	while counter < 5:
		try:
			# Inicia uma ligacao com timeout de 5 sec
			res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'}, timeout=5)
			soup = BeautifulSoup(res.text,"lxml")
			
			# Faz um scan a pag e guarda os ips/ports na lista
			for items in soup.select("tbody tr"):
				proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
				proxies.append(proxy_list)
				
			if len(proxies) != 0:
				# Retorna um ip/port aleatorio da lista
				return random.choice(proxies)
		
		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
			#print "ProxyError..."
			counter += 1
	
	return None
	

def getFile(url, file, proxy):
	if proxy:
		file = "feeds/" + file
		
	# Se o ficheiro ja existir, elimina-o
	if os.path.exists(file):
		#print "delete...",file
		os.remove(file)
	
	# Inicializa o counter e o
	# dicionario de proxy
	counter = 0
	proxy_dict = {}
	
	# Enquanto o ficheiro nao existir e o
	# Contador for inferior a 5
	while ((os.path.exists(file)) == False) and (counter < 5):
		#print counter
		
		try:
			#print "downloading..."
			
			# Se proxy = True, gera um proxy
			if proxy:
				proxy_dict = {"http": getProxy()}
			
			# Faz uma ligacao ao url, com timeout de 5 secs
			r = requests.get(url, proxies = proxy_dict, timeout=5)
			
			# Escreve o conteudo no ficheiro xml
			with open(file, 'wb') as f:  
				f.write(r.content)
			f.close()
			
		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
			#print "error..."
			counter += 1
	
	if os.path.exists(file):
		return True
	
		
def checkRss(curso):
	
	# Abre o ficheiro de log e guarda a data da ultima publicacao
	with open("archive/" + curso + ".txt", 'r') as log:
		lastPublished = log.readline()
	log.close()
	print "Ultima data...",lastPublished

	# Abre o xml
	feed = feedparser.parse("feeds/" + curso + ".xml")

	content = range(3)
	
	# Percorre os posts
	for post in feed.entries:
		# Converte a data para o formato correto
		tmpPublished = str(datetime.datetime.strptime(post.published, "%a, %d %b %Y %H:%M:%S %Z"))
		#print "Data...",tmpPublished
		
		if tmpPublished > lastPublished:
			lastPublished = tmpPublished
			title = post.title.encode('utf-8')
			description = post.description.encode('utf-8')
			
			# Cria uma lista com o conteudo
			# Indice 0 = Titulo em UTF-8
			# Indice 1 = Descricao convertido em UTF-8
			content[0] = lastPublished
			content[1] = title
			content[2] = description
	
	#print content
	if content[0] != 0:
		return content
	
	return None


def writeLog(curso, content):
	# Abre o ficheiro de arquivo
	with open("archive/" + curso + ".txt", "r") as log:
		old = log.read()
	log.close()

	with open("archive/" + curso + ".txt", "w") as log:
		log.write(content[0])
		log.write("\n" + content[1])
		log.write("\n" + content[2])
		log.write("\n-----------------------\n")
		log.write(old)
	log.close()
	

def csvReader(curso, file):
	mailList = list()
	
	with open(file, 'rb') as fp:
		reader = csv.reader(fp)
		allMails = list(reader)
	fp.close()
	
	for entry in allMails:
		if entry[2] == curso:
			mailList.append(entry[1])
			
	return mailList
	

def sendMail(text, mail):
	fromaddr = "edersemelhante@gmail.com"
	toaddr = mail
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ", ".join(mail) 
	msg['Subject'] = text[1]
	
	msg.attach(MIMEText(text[2] + "<br><br><p>- - - - - - - -<br>Para deixar de receber estes emails, entre \
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
	

if __name__ == '__main__':
	#os.system("clear")
	
	# TESTES
	cursos = ["TIC", "EINF", "CMU", "EME", "ECN", "GES", "LRE", "PSI"]
	mailUrl = "https://docs.google.com/spreadsheets/u/0/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv"
		
	# REAL
	#cursos = ["TIC", "EINF", "CMU", "EME", "ECN", "GES", "LRE", "PSI"]
	#mailUrl = "https://docs.google.com/spreadsheets/d/1HUFRioP96WZCZWaTR3bfTQeOg472dQyyGXrPzE4Nl3M/export?format=csv"
	
	while True:
		for curso in cursos:
			print curso,"..."
			feedFile = curso + ".xml"
			feedUrl = "http://side.utad.pt/rss.pl?" + curso
		
			getFile(feedUrl, feedFile, True)
			if os.path.exists("feeds/" + feedFile):
				content = checkRss(curso)
				if content:
					mailFile = "mails.csv"
					getFile(mailUrl, mailFile, False)
					sendMail(content, csvReader(curso, mailFile))
					writeLog(curso, content)
			
			print "\n"
			
	