from collections import Counter
import textract
import json
import aws_bucket
import aws_sqs
# Install from http://textract.readthedocs.io/en/latest/installation.html
def getRepeatedWord(filePath):
	words = Counter(textract.process(filePath).split())
	return max(words, key=words.get),words.get(max(words, key=words.get))

def addFindex(key,tag,n):
	d = dict()
	with open(index) as f:
		data = json.load(f)
	if tag in data:
		d = data.get(tag)
		d[key] = n
		data[tag] = d
	else:
		d[key] = n
		data[tag] = d

	with open(index, 'w') as outfile:
		json.dump(data, outfile)

def addToken():
	att = {'Type':{'DataType':'String','StringValue':'Token'}}
	mes = 'Token message'
	aws_sqs.put_message(turl,mes,att)

index = 'Findex.json'
bname = 'l-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)


while True:
	m = None
	while m is None:
		try:
			messages = aws_sqs.read_message(iurl)
			m = messages['Messages'][0]
		except:
			m = None		
	typem = m['MessageAttributes']['Type']['StringValue']
	if typem =='Tagging':
		print('Tagging message received')
		clientid = m['MessageAttributes']['ClientId']['StringValue']
		key = m['Body']
		rhandle = m['ReceiptHandle']
		#Get the document form the bucket
		filename = key
		aws_bucket.get_doc_bucket(bname,filename,key)
		tag,n = getRepeatedWord(filename)
		print('The tag of the file is '+tag)
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
		print('Token received')
		aws_bucket.get_doc_bucket(bname,index,index)
		addFindex(key,tag,n)
		aws_bucket.upload_doc_bucket(bname,index,index)
		addToken()
		#Send message to the client
		mes = tag
		att = {'Type':{'DataType':'String','StringValue':'Tagging Response'},
				'ClientId':{'DataType':'String','StringValue':str(clientid)}
				}
		aws_sqs.put_message(ourl,mes,att)		
		aws_sqs.delete_message(iurl,rhandle)
		print('Tagging response send')
	
