import aws_bucket
import aws_sqs
import json
import operator

index = 'Findex.json'
bname = 'l-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)

def findIndex(tag):
	d = dict()
	with open(index) as f:
		data = json.load(f)
	if tag in data:
		d = data[tag]
		s = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
		docs = s	
	else:
		docs = None
	return docs	

def addToken():
	att = {'Type':{'DataType':'String','StringValue':'Token'}}
	mes = 'Token message'
	aws_sqs.put_message(turl,mes,att)
	
while True:
	m = None
	while m is None:
		try:
			messages = aws_sqs.read_message(iurl)
			m = messages['Messages'][0]
			rhandle = m['ReceiptHandle']
			aws_sqs.change_vis(iurl, rhandle, 20)
		except:
			m = None	
	typem = m['MessageAttributes']['Type']['StringValue']
	if typem =='Searching':
		aws_sqs.change_vis(iurl, rhandle, 200)
		print('Message of Searching received')	
		clientid = m['MessageAttributes']['ClientId']['StringValue']
		tag = m['Body']
		rhandle = m['ReceiptHandle']	
		#Get the token
		mtoken = None
		while (mtoken is None):
			try:
				messages = aws_sqs.read_message(turl)
				mtoken = messages['Messages'][0]
			except:
				mtoken = None
		print('Token received')			
		rh = mtoken['ReceiptHandle']
		aws_sqs.delete_message(turl,rh)
		docs = findIndex(tag)
		addToken()
		#Send message to the client
		mes = str(docs)
		att = {'Type':{'DataType':'String','StringValue':'Searching Response'},
				'ClientId':{'DataType':'String','StringValue':str(clientid)}
				}
		r = None
		while r is None:		
			r = aws_sqs.put_message(ourl,mes,att)
		print('Searching response send')		
		aws_sqs.delete_message(iurl,rhandle)
	
	
