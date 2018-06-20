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
import random


index = 'Findex.json'
bname = 'lo-ta-bucket-p1'
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
		for i in docs:
			s = i[0].split('_')
			if s[1] not in g:
				g.append(s[1])
				key = s[1]
				aws_bucket.get_doc_bucket(bname,key,i[0])
			else:
				r = str(random.randint(1,1001))
				key = r+s[1]
				aws_bucket.get_doc_bucket(bname,key,i[0])	
		print('\nFiles downloaded\n')	
		
def printDocs(docs):
	docs_aux = []
	g = []
	urls = []
	docs = ast.literal_eval(docs)
	if docs is None:
		print('There are no files for that tag\n')
	else:
		print('The files are:\n')
		for i in docs:
			s = i[0].split('_')
			if s[1] not in g:
				g.append(s[1])
				print('\t'+s[1]+'\n')
				u = aws_bucket.get_url(bname,i[0])
				docs_aux.append(s[1])
				urls.append(u)
			else:
				r = str(random.randint(1,1001))
				print('\t'+r+s[1]+'\n')
				u = aws_bucket.get_url(bname,i[0])
				docs_aux.append(r+s[1])	
				urls.append(u)
		return docs_aux,urls

def tagFile(filename):
	clientID =  cherrypy.session.id
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
			if clientid == clientID:
				aws_sqs.change_vis(ourl, rhandle, 20)
				print('Tagging response received\n')	
				tag = m['Body']
				addTags(tag)
				aws_sqs.delete_message(ourl,rhandle)
				print('The tag is: '+tag+'\n\n')
				send = True
				return tag
				
			else:
				send = False
				
def searchTag(tag):
	clientID =  cherrypy.session.id
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
			if clientid == clientID:
				aws_sqs.change_vis(ourl, rhandle, 100)
				print('Searching response received\n')	
				docs = m['Body']
				aws_sqs.delete_message(ourl,rhandle)
				docs_aux = printDocs(docs)
				send = True
				return docs_aux
			else:
				send = False

def listTags():
	clientID =  cherrypy.session.id
	try:
		with open(clientID+'tags.json') as f:
			data = json.load(f)
		return data['tags']
	except:
		print('There are not previous tags\n')	
		return None

def addTags(tag):
	clientID =  cherrypy.session.id
	try:
		with open(clientID+'tags.json') as f:
			data = json.load(f)
	except:	
			data = dict()
			data['tags'] = []
	if tag not in data['tags']:
		data['tags'].append(tag)
	with open(clientID+'tags.json', 'w') as outfile:
		json.dump(data, outfile)

class ClientWeb(object):


	@cherrypy.expose
	def index(self):
		addTags('')
		clientID =  cherrypy.session.id
		print(clientID)
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
					<h2>Tag result</h2>
					The file that is being tagging is: {file:}<br><br>
					The getting tag is: {tag}
					</body></html>""".format(file=file,tag=tag)
		return out					

	@cherrypy.expose
	def searching(self, tag):
		"Main menu to select interest"
		reader = codecs.getreader("utf-8")
		if file is not None: 
			docs,urls = searchTag(tag)
		out = """<html><body>
				<h2>Search result</h2>
				The tag you are searching for is: {tag:}<br><br>
				The files for that tag are: {docs:} <br><br>
				Download the files in: {urls:} <br><br>
				</body></html>""".format(tag=tag,docs=', '.join(docs),urls=', '.join(urls)) 
		return out	

	@cherrypy.expose
	def listTags(self):
		"Main menu to select interest"
		tags = listTags()
		reader = codecs.getreader("utf-8")
		out = """<html><body>
				<h2>Tags</h2>
				{tags:}	
				</body></html>""".format('\n'.join(tags))
		return out	


cherrypy.config.update({'tools.sessions.on': True                           
               })

if __name__ == '__main__':
	cherrypy.quickstart(ClientWeb())
