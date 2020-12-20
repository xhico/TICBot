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
from itertools import izip
from bs4 import BeautifulSoup
from collections import Counter
from multiprocessing import Process
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart


def getProxy():
	if debug: print "Proxy..."
	
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
			if debug: print "ProxyError..."
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
	#print "Ultima data...",lastPublished

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


	old = list()
	recordsFile = "records.txt"
	numbLines = sum(1 for line in open(recordsFile))
	linesToKeep = 100

	with open(recordsFile, "r") as fp:
		if numbLines + 1 > linesToKeep:
			for line in fp.readlines()[0:linesToKeep - 1]:
				old.append(line)
		else:
			for line in fp.readlines():
				old.append(line)
	fp.close()

	with open(recordsFile, "w") as fp:
		fp.write(content[0] + "\n")
		for line in old:
			fp.write(line)
	fp.close()
	

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
	
	#fp = open('eder.jpg', 'rb')
	#msgImage = MIMEImage(fp.read())
	#fp.close()
	#msgImage.add_header('Content-ID', '<image1>')
	#msg.attach(msgImage)
	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "Edersemelhante1")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()


def dataFileReader(file):
	if debug:
		print "---------------"
		print "Reading..."

	lines = list()
	with open(file, "r") as fp:
		for line in fp.readlines():
			lines.append(line.split(" ")[1].split("\n")[0])
	fp.close()

	return lines


def dataFileAnalizer(hourList):
	if debug:print "---------------\nAnalizing..."
	tmpHourList = list()
	k = 12

	for hour in hourList:
		tmpHourList.append(int(hour.split(":")[0]))

	most_common = [key for key, val in Counter(tmpHourList).most_common(k)]
	nowHour = datetime.datetime.now().hour

	if debug: print "---------------\n",most_common
	return nowHour in most_common


def getCursos(file):
	with open(file, "r") as fp:
		tmpCursos = fp.readlines()
	fp.close()

	cursos = list()
	for curso in tmpCursos:
		cursos.append(curso.replace("\n", "").split(" ")[0])

	for curso in cursos:
		if not os.path.exists("archive/" + curso + ".txt"):
			with open("archive/" + curso + ".txt", "w") as fp:
				fp.write("0000-00-00 00:00:00")
			fp.close()

	return cursos


def launcher(curso, mailFile):
	if debug: print "start",curso,"..."
	feedFile = curso + ".xml"
	feedUrl = "http://side.utad.pt/rss.pl?" + curso


	mails = csvReader(curso, mailFile)
	
	if len(mails) > 0:
		getFile(feedUrl, feedFile, True)
		
		if os.path.exists("feeds/" + feedFile):
			content = checkRss(curso)
			
			if content:
				sendMail(content, mails)
				writeLog(curso, content)
				
	if debug: print "end",curso,"..."


debug = True
if __name__ == '__main__':

    if debug: os.system("clear")
    recordsFile = "records.txt"
    cursosFile = "cursos.txt"

    # TESTES
    mailUrl = "https://docs.google.com/spreadsheets/u/0/d/1hRDwiwo85bgMp2m9CIpKKCAL_90tPVgIbiz2zvrjXqA/export?format=csv"

    # REAL
    #mailUrl = "https://docs.google.com/spreadsheets/d/1HUFRioP96WZCZWaTR3bfTQeOg472dQyyGXrPzE4Nl3M/export?format=csv"


    cursos = getCursos(cursosFile)
    threads = 4
    tmpCursos = [cursos[i * threads:(i + 1) * threads] for i in range((len(cursos) + threads - 1) // threads )]

    while True:
        Pros = []
        mailFile = "mails.csv"
        getFile(mailUrl, mailFile, False)
        
        for set in tmpCursos:
            for curso in set:
                p = Process(target=launcher, args=(curso,mailFile,))
                Pros.append(p)
                p.start()
        
            for t in Pros:
                t.join()
        
            if debug: print "---------------"

        #if not dataFileAnalizer(dataFileReader(recordsFile)): secs = 15*60
        #else: ecs = 2
            
        #if debug: print "Sleeping " + str(secs) + "..."
        time.sleep(2)
