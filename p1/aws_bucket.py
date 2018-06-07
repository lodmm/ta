import boto3
import botocore

#lorena-bucket
def create_bucket(name):
  s3 = boto3.client('s3')
  s3.create_bucket(Bucket=name)

def upload_doc_bucket(name, filename, key):
	s3 = boto3.client('s3')
	s3.upload_file(filename,name,key)

def get_doc_bucket(name,filename,key):
	s3 = boto3.resource('s3')
	try:
		s3.Bucket(name).download_file(key, filename)
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object doesn't exist")


			
#upload_doc_bucket('lorena-bucket','doc.txt','doc1')
#get_doc_bucket('lorena-bucket','doc1.txt','doc1')
#get_doc_bucket('lorena-bucket','doc2.txt','Docs')

