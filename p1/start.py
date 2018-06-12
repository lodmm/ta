import aws_bucket
import aws_sqs

def addToken():
	att = {'Type':{'DataType':'String','StringValue':'Token'}}
	mes = 'Token message'
	aws_sqs.put_message(turl,mes,att)
#Create the bucket
bname = 'l-ta-bucket-p1'
bucket = aws_bucket.create_bucket(bname)
print(bname," created")
#Create the queues 
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iq = aws_sqs.create_queue(inbox)
oq = aws_sqs.create_queue(outbox)
tq = aws_sqs.create_queue(qtoken)
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)
print("Queues inbox, outbox and trafficl created")
#Sending the token 
addToken()
#Adding the index file to the bucket
file = 'Findex.json'
f = open(file,"w")
aws_bucket.upload_doc_bucket(bname,file,file)
#Ec2 instances


