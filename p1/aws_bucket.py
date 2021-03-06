import boto3
import re
import botocore


def create_bucket(name):
  s3 = boto3.client('s3')
  s3.create_bucket(Bucket=name)

def upload_doc_bucket(name, filename, key):
	s3 = boto3.client('s3')
	s3.upload_file(filename,name,key)

def get_doc_bucket(name,filename,key):
	s3 = boto3.resource('s3')
	try:
		open(filename,"w+")
		s3.Bucket(name).download_file(key, filename)
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object doesn't exist")

def delete_bucket(name):
	s3 = boto3.client('s3')
  	s3.delete_bucket(Bucket=name)

def get_url(bname,key):
	# Get the service client.
	s3 = boto3.client('s3')
	# Generate the URL to get 'key-name' from 'bucket-name'
	url = s3.generate_presigned_url(
	    ClientMethod='get_object',
	    Params={
	        'Bucket': bname,
	        'Key': key
	    }
	)
	return url

def delete_doc(bucket,key):
	s3 = boto3.resource('s3')
	s3.Object(bucket,key).delete()	

#def get_docs(bucket):
	
