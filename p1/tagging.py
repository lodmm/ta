from collections import Counter
import textract
import aws_bucket
import aws_sqs
# Install from http://textract.readthedocs.io/en/latest/installation.html
def getRepeatedWord(filePath):
	words = Counter(textract.process(filePath).split())
	return max(words, key=words.get)
	
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
	


