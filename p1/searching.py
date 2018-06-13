import aws_bucket
import aws_sqs
import json

index = 'Findex.json'
bname = 'l-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)

def findIndex(tag):
	with open(index) as f:
		data = json.load(f)
	if tag in data:
		docs = data[tag]
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
		except:
			m = None		
	typem = m['MessageAttributes']['Type']['StringValue']
	if typem =='Searching':
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
		rh = mtoken['ReceiptHandle']
		aws_sqs.delete_message(turl,rh)
		docs = findIndex(tag)
		addToken()
		#Send message to the client
		mes = docs
		att = {'Type':{'DataType':'String','StringValue':'Searching Response'},
				'ClientId':{'DataType':'String','StringValue':str(clientid)}
				}
		aws_sqs.put_message(ourl,mes,att)		
		aws_sqs.delete_message(iurl,rhandle)
	else:
		print('The message is not for searching')	
	
