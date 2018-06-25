import json
import sys
import ast
import aws_bucket
import aws_sqs
import os
import signal
import random

switcher = {
        1: "Tagging",
        2: "Searching",
        3: "List tags",
        4: "Exit"
    }

clientID =  os.getpid()
index = 'Findex.json'
bname = 'l-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)

def downloadFiles(docs):
	docs = ast.literal_eval(docs)
	g = []
	if docs is not None:
		print('The files are:\n')
		for i in docs:
			s = i[0].split('_')
			if s[1] not in g:
				g.append(s[1])
				key = s[1]
				aws_bucket.get_doc_bucket(bname,key,i[0])
				print('\t'+s[1]+'\n')
			else:
				r = str(random.randint(1,1001))
				key = r+s[1]
				aws_bucket.get_doc_bucket(bname,key,i[0])
				print('\t'+r+s[1]+'\n')	
		print('\nFiles downloaded\n')	
	else:
		print('There are no files for that tag\n')


def tagFile(filename):
	dfilename = str(clientID) + '_' + filename
	aws_bucket.upload_doc_bucket(bname, filename, dfilename)
	att = {'Type':{'DataType':'String','StringValue':'Tagging'},'ClientId':{'DataType':'String','StringValue':str(clientID)}}
	body = dfilename
	r = None
	while r is None:		
		r = aws_sqs.put_message(iurl,body,att)
	print('Message for tagging sent\n')
	send = False
	while send is False:
		m = None
		while m is None:
			try:
				messages = aws_sqs.read_message(ourl)
				m = messages['Messages'][0]
				rhandle = m['ReceiptHandle']
				aws_sqs.change_vis(ourl, rhandle, 40)
			except:
				m = None		
		typem = m['MessageAttributes']['Type']['StringValue']
		if typem =='Tagging Response':
			clientid = m['MessageAttributes']['ClientId']['StringValue']
			if clientid == str(clientID):
				aws_sqs.change_vis(ourl, rhandle, 20)
				print('Tagging response received\n')	
				tag = m['Body']
				addTags(tag)
				aws_sqs.delete_message(ourl,rhandle)
				print('The tag is: '+tag+'\n\n')
				send = True
			else:
				send = False

def searchTag(tag):
	att = {'Type':{'DataType':'String','StringValue':'Searching'},'ClientId':{'DataType':'String','StringValue':str(clientID)}}
	body = tag
	r = None
	while r is None:		
		r = aws_sqs.put_message(iurl,body,att)
	print('Message for searching sent\n')
	send = False
	while send is False:
		m = None
		while m is None:
			try:
				messages = aws_sqs.read_message(ourl)
				m = messages['Messages'][0]
				rhandle = m['ReceiptHandle']
				aws_sqs.change_vis(ourl, rhandle, 40)
			except:
				m = None		
		typem = m['MessageAttributes']['Type']['StringValue']
		if typem =='Searching Response':
			clientid = m['MessageAttributes']['ClientId']['StringValue']
			if clientid == str(clientID):
				aws_sqs.change_vis(ourl, rhandle, 100)
				print('Searching response received\n')	
				docs = m['Body']
				aws_sqs.delete_message(ourl,rhandle)
				downloadFiles(docs)
				send = True
			else:
				send = False

def clearTags():
	try:
		with open('tags.json') as f:
			data = json.load(f)
		data['tags'] = []
		with open('tags.json', 'w') as outfile:
			json.dump(data, outfile)
		print('\nTags list removed\n')	
	except:	
		print('\nTags list removed\n')

def signal_handler(signum, frame):
	sys.exit(0)

def listTags():
	try:
		with open('tags.json') as f:
			data = json.load(f)
		return data['tags']
	except:
		print('There are not previous tags\n')	
		return None

def addTags(tag):
	try:
		with open('tags.json') as f:
			data = json.load(f)
	except:	
			data = dict()
			data['tags'] = []
	if tag not in data['tags']:
		data['tags'].append(tag)
	with open('tags.json', 'w') as outfile:
		json.dump(data, outfile)

def switch_demo(argument):
    print ('\n Your option is '+switcher.get(argument, "Invalid")+'\n')


while True:
	try:
		argument = raw_input('\n\nWhat do you want to do?:\n1.'+switcher.get(1)+
			'\n2.'+switcher.get(2)+'\n3.'+switcher.get(3)+
			'\n4.'+switcher.get(4)+
			'\n\n') 
		switch_demo(int(argument))
	except:
		print('\n\nInvalid select\n\n')	
		break
	if int(argument) is 1:
		filename = raw_input('\nIntroduce the name of the file you want to tag:\n')
		tagFile(filename)
	else:
		if int(argument) is 2:
			tag = raw_input('\nIntroduce the tag you want to search:\n')
			searchTag(tag)
		else:
			if int(argument) is 3:		
				tags = listTags()
				if tags is not None:
					for i in tags: print(i+"\n")
			else:
				if int(argument) is 4:		
					break