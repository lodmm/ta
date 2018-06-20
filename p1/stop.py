import aws_bucket
import aws_sqs


bname = 'lo-ta-bucket-p1'
inbox = 'inbox'
outbox = 'outbox'
qtoken = 'token'
iurl = aws_sqs.get_url(inbox)
ourl = aws_sqs.get_url(outbox)
turl = aws_sqs.get_url(qtoken)

#Deleting the inndex file of the bucket

#Ec2 instances	
#Delete the bucket

#Delete queues
aws_sqs.delete_queue(iurl)
aws_sqs.delete_queue(ourl)
aws_sqs.delete_queue(turl)
print("Queues inbox, outbox and trafficl deleted")
