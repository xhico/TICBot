#-*- coding: utf-8 -*-
#!/usr/bin/env python2



def write(file, data, text):
	with open("archive/" + curso + ".txt", 'r') as log:
		pubTime = log.readline()
		print pubTime
	log.close()
	
	
curso = "TIC"
data = "2018-10-02 11:08:32"
text = "hello world"
write(curso, data, text)