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

def delete_queue(urln):
	sqs = boto3.client('sqs')
	try:
		sqs.delete_queue(QueueUrl=urln)	
	except Exception as e:
		print("The queue does not exist")	

def put_message(urln, message, attributes):
	sqs = boto3.client('sqs')
	try:	
		response = sqs.send_message(
			QueueUrl = urln,
			MessageBody = message,
			MessageAttributes = attributes	
		)
	except Exception as e:
		print("It is not possible to put the message")

def read_message(urln):
	sqs = boto3.client('sqs')
	try:	
		response = sqs.receive_message(
			QueueUrl = urln,
			AttributeNames=[
		        'SentTimestamp'
		    ],
		    MaxNumberOfMessages=10,
		    MessageAttributeNames=[
		        'All'
		    ],
		    VisibilityTimeout=0,
		    WaitTimeSeconds=0
		)
	except Exception as e:
		print(e)
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

def get_url_queue(name):
	sqs = boto3.client('sqs')
	try:
		urln = None	
		response = sqs.get_queue_url(QueueName=name)
		urln = response['QueueUrl']
	except 	Exception as e:
		print("The queue does not exist")

	return urln

def list_queues():
	sqs = boto3.client('sqs')
	response = sqs.list_queues()
	return response