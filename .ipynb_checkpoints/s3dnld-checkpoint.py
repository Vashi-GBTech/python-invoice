import boto3
import os
from constants import *

client = boto3.client("s3", 
                      aws_access_key_id ='AKIA3ORLNQH5YVFYKW5T',
                      aws_secret_access_key ='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', 
                      )

bucket_name = "rmt-bucket-ecovisrkca"

list_files = client.list_objects(Bucket=bucket_name)['Contents']
#print(list_files)

root_path = os.getcwd()

for key in list_files:
    
    download_file_path = os.path.join(root_path, "downloads", key['Key'])
    
    client.download_file(
        Bucket = bucket_name,
        Key = key['Key'],
        Filename = download_file_path    
    )

