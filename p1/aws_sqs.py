import boto3
import botocore

#lorena-queue

def create_queue(name):
	sqs = boto3.client('sqs')
	response = sqs.create_queue(
    QueueName= name,
    Attributes={
        'DelaySeconds': '60',
        'MessageRetentionPeriod': '86400'
    })

def delete_queue(name):
	sqs = boto3.client('sqs')
	urln = get_url_queue(name)
	if urln != NUll:
		sqs.delete_queue(QueueUrl=urln)
	else:
		print('It is not possible to delete the queue')		

def put_message(urln, message, attributes,delay,did,gid):
	sqs = boto3.client('sqs')
	try:	
		response = sqs.send_message(
			QueueUrl = urln,
			MessageBody = message,
			DelaySeconds = delay,	
			MessageAttributes = attributes,
			MessageDuplicationId = did,
			MessageGroupId = gid
		)
	except Exception as e:
		print("It is not possible to put the message")

def read_message(urln, attnames, attributes, vis, timeseconds, iid):
	sqs = boto3.client('sqs')
	try:	
		response = sqs.receive_mesage(
			QueueUrl = urln,
			AttributesNames = attnames,	
			MessageAttributesNames = attributes,
			VisibilityTimeout = vis,
			WaitTimeSeconds = timeseconds,
			ReceiveRequestAttemptId = iid
		)
	except Exception as e:
		print("It is not possible to read the message")

def delete_message(urln, rhandle):
	sqs = boto3.client('sqs')
	try:
	response = sqs.delete_message(
		QueueUrl = urln,
		ReceiptHandle=rhandle)
	except Exception as e:
		print("It is not possible to delete the message")

def change_vis(urln, rhandle, vis):
	sqs = boto3.client('sqs')
	try:
	response = sqs.delete_message(
		QueueUrl = urln,
		ReceiptHandle=rhandle,
		VisibilityTimeout = vis
		)
	except Exception as e:
		print("It is not possible to change the visibility of the message")

def enable_long_polling(urln):
	sqs = boto3.client('sqs')

def get_url_queue(name):
	sqs = boto3.client('sqs')
	urln = NULL
	try:
		response = sqs.get_queue_url(QueueName=name)
		urln = response['QueueUrl']
	except 	Exception as e:
		print("The queue does not exist")

	return urln

