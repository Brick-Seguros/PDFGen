import boto3
import os

brck_u=os.environ.get('BRCK_U')
brck_p=os.environ.get('BRCK_P')
skid=os.environ.get('SKID')
sksec=os.environ.get('SKSEC')

session = boto3.Session(
    aws_access_key_id=skid,
    aws_secret_access_key=sksec
)
s3 = session.resource('s3')

