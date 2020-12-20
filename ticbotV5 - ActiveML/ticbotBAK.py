#-*- coding: utf-8 -*-
#!/usr/bin/python

import smtplib
import os
import time
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders

# sudo apt-get install zip

def createBAK(file):
	cmd = str("zip -r -q " + file + " /home/pi/ticbot")
	os.system(cmd)
	
	return file
	
	
def removeBAK(file):
	cmd = str("rm -rf " + file)
	os.system(cmd)	
	
	
def send_mail(file):
	# Envia mail com o IP, Hostname e data

	fromaddr = "other.coisas@gmail.com"
	toaddr = "edersemelhante@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "ticbotBAK"
	
	body = ""
	msg.attach(MIMEText(body, 'plain'))

	part = MIMEBase('application', "octet-stream")
	part.set_payload(open(file, "rb").read())
	Encoders.encode_base64(part)

	str = "attachment; filename=" + file
	part.add_header('Content-Disposition', str)

	msg.attach(part)
	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "othercoisas")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	
	

now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file = "/home/pi/ticbot_" + now + ".zip"

createBAK(file)
send_mail(file)
removeBAK(file)
while True:
	if (datetime.datetime.now().hour == 00) or (datetime.datetime.now().hour == 12):
		createBAK(file)
		send_mail(file)
		removeBAK(file)
		time.sleep(43200)




