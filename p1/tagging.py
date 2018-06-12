from collections import Counter
import textract
import json
import aws_bucket
import aws_sqs
# Install from http://textract.readthedocs.io/en/latest/installation.html
def getRepeatedWord(filePath):
	words = Counter(textract.process(filePath).split())
	return max(words, key=words.get)

def addFindex(key,tag):
	
	with open(index) as f:
		data = json.load(f)

    if tag in data:
    	data[tag].append(key)
    else:
    	data[tag] = [key]

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
		clientid = m['MessageAttributes']['ClientId']['StringValue']
		key = m['Body']
		rhandle = m['ReceiptHandle']
		#Get the document form the bucket
		filename = key
		aws_bucket.get_doc_bucket(bname,filename,key)
		tag = getRepeatedWord(filename)
		#Get the token
		mtkone = None
		while (mtoken is None):
			mtoken = aws_sqs.read_message(turl)
		rh = mtoken['Messages'][0]['ReceiptHandle']
		aws_sqs.delete_message(turl,rh)
		aws_bucket.get_doc_bucket(bname,index,index)
		addFindex(key,tag)
		aws_bucket.upload_doc_bucket(bname,index,index)
		addToken()
		#Send message to the client
		mes = tag
		att = {'Type':{'DataType':'String','StringValue':'Tagging Response'},
				'ClientId':{'DataType':'String','StringValue':clientid}
				}
		aws_sqs.put_message(ourl,mes,att)		
		aws_sqs.delete_message(iurl,rhandle)
	else:
		print('The message is not for tagging')	
