import boto3

s3 = boto3.client('s3')
s3.create_bucket(Bucket='Lorena_bucket')

response = s3.list_buckets()

buckets = [bucket['Name'] for bucket in response['Buckets']]

print("Bucket List %s" buckets)
