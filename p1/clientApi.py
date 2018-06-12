import json
import sys
import aws_bucket
import aws_sqs
import os

switcher = {
        1: "Tagging",
        2: "Searching",
        3: "List tags",
        4: "Remove tag list",
        5: "Exit"
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

def tagFile(filename):
	aws_bucket.upload_doc_bucket(bname, filename, filename)
	att = {'Type':{'DataType':'String','StringValue':'Tagging'},
				'ClientId':{'DataType':'String','StringValue':clientID}}
	body = filename			
	aws_sqs.put_message(outfile,body,att)

	addTags('')

def searchTag(tag):
	print tag

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
		print('There are not previous tags')	
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
    print ('\n'+switcher.get(argument, "Your option is Invalid")+'\n')


while True:
	try:
		argument = raw_input('What do you want to do?:\n1.'+switcher.get(1)+
			'\n2.'+switcher.get(2)+'\n3.'+switcher.get(3)+
			'\n4.'+switcher.get(4)+
			'\n5.'+switcher.get(5)+'\n\n') 
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
					clearTags()
				else:
					if int(argument) is 5:		
						break