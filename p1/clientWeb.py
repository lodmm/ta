#!/usr/bin/env python
import cherrypy
import codecs
import json
import sys
import ast
import aws_bucket
import aws_sqs
import os
import signal


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
	for i in docs:
		open(i)
		aws_bucket.get_doc_bucket(bname,i,i)
	print('\nFiles downloaded\n')	

def printDocs(docs):
	docs = ast.literal_eval(docs)
	if docs is None:
		print('There are no files for that tag\n')
	else:
		print('The files are:\n')
		for i in docs:
			print('\t'+i+'\n')

def tagFile(filename):
	aws_bucket.upload_doc_bucket(bname, filename, filename)
	att = {'Type':{'DataType':'String','StringValue':'Tagging'},'ClientId':{'DataType':'String','StringValue':str(clientID)}}
	body = filename
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
			except:
				m = None		
		typem = m['MessageAttributes']['Type']['StringValue']
		if typem =='Tagging Response':
			clientid = m['MessageAttributes']['ClientId']['StringValue']
			if int(clientid) == clientID:
				print('Tagging response received\n')	
				tag = m['Body']
				rhandle = m['ReceiptHandle']
				addTags(tag)
				aws_sqs.delete_message(ourl,rhandle)
				print('The tag is: '+tag+'\n\n')
				send = True
				return tag
				
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
			except:
				m = None		
		typem = m['MessageAttributes']['Type']['StringValue']
		if typem =='Searching Response':
			clientid = m['MessageAttributes']['ClientId']['StringValue']
			if int(clientid) == clientID:
				print('Searching response received\n')	
				docs = m['Body']
				rhandle = m['ReceiptHandle']
				aws_sqs.delete_message(ourl,rhandle)
				printDocs(docs)
				downloadFiles(docs)
				send = True
				return docs
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

class ClientWeb(object):


	@cherrypy.expose
	def index(self):
		return """<html>
			<head></head>
			<body>
			<h1>Client Application</h1>
			<h2>Tagging a file</h2>
			<form method="post" enctype="multipart/form-data" action="tagging"">
				<input type="text" name="file" id="file"/><br><br>
				<input type="submit" value="Start">
			</form>
			<h2>Searching a tag</h2>
			<form method="post" action="searching" ">
				<input type="text" name="tag" id="tag"><br><br>
				<input type="submit" value="Start">
			</form>	
			<h2>List tags</h2>
			<form method="post" action="listTags" ">
				<input type="submit" value="List"><br><br>
			</form>	
			<h2>Clear tags</h2>
			<form method="post" action="clearTags" ">
				<input type="submit" value="Clear" ><br><br>
			</form>		
			</body>
			</html>"""

	@cherrypy.expose
	def tagging(self, file):
		"Main menu to select interest"
		reader = codecs.getreader("utf-8")
		if file is not None: 
			tag = tagFile(file)
			print(file)
			out = """<html><body>
					<h2>Waiting for the the tag result</h2>
					The file that is being tagging is: {file:}<br><br>
					The getting tag is: {tag}
					</body></html>""".format(file=file,tag=tag)
		return out					

	@cherrypy.expose
	def searching(self, tag):
		"Main menu to select interest"
		reader = codecs.getreader("utf-8")
		if file is not None: 
			docs = searchTag(tag)
			print(tag)
		out = """<html><body>
				<h2>Waiting for the the search result</h2>
				The tag you are searching for is: {tag:}<br><br>
				The files for that tag are: {docs:}
				</body></html>""".format(tag=tag,docs=docs) 
		return out	

	@cherrypy.expose
	def listTags(self):
		"Main menu to select interest"
		reader = codecs.getreader("utf-8")
		out = """<html><body>
				<h2>Tags</h2>
				</body></html>"""
		return out	

	@cherrypy.expose
	def clearTags(self):
		"Main menu to select interest"
		reader = codecs.getreader("utf-8")
		out = """<html><body>
				<h2>The list of tags was cleared</h2>
				</body></html>"""
		return out					
				



if __name__ == '__main__':
	cherrypy.quickstart(ClientWeb())
