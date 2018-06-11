import aws_bucket
import aws_sqs
import tag

index = 'Findex.json'
bname = 'l-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url_queue(inbox)
ourl = aws_sqs.get_url_queue(outbox)
turl = aws_sqs.get_url_queue(qtoken)

while True:
	messages = aws_sqs.read_message(iurl)
	
