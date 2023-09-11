"""
Functionality of S3
"""

import boto3
from botocore.exceptions import ClientError
from libdev.cfg import cfg
from libdev.gen import generate


LINK = 'https://s3.chill.services/'


s3 = boto3.resource(
    's3',
    endpoint_url=LINK,
    aws_access_key_id=cfg('s3.user'),
    aws_secret_access_key=cfg('s3.pass'),
    region_name='us-east-1',
)
s3client = s3.meta.client


def upload_file(
    file,
    directory=cfg('mode'),
    bucket=cfg('project_name'),
):
    """ Upload file """

    file_type = file.split('.')[-1]
    name = f"{directory}/{generate()}.{file_type}"

    s3client.upload_file(
        file, bucket, name,
        ExtraArgs={'ACL': 'public-read'},
    )

    return f"{LINK}{bucket}/{name}"

def get_policy(bucket=cfg('project_name')):
    """ Get bucket policy """
    return s3client.get_bucket_policy(Bucket=bucket)


__all__ = (
    's3',
    's3client',
    'ClientError',
    'upload_file',
    'get_policy',
)
