"""
Functionality of Amazon Web Services
"""

import boto3
from botocore.exceptions import ClientError
from libdev.cfg import cfg
from libdev.gen import generate


LINK = (
    f"https://{cfg('amazon.bucket')}.s3."
    f"{cfg('amazon.region')}.amazonaws.com/"
)


s3 = boto3.resource(
    's3',
    region_name=cfg('amazon.region'),
    aws_access_key_id=cfg('amazon.key'),
    aws_secret_access_key=cfg('amazon.secret'),
)
s3client = s3.meta.client


def upload_file(
    file,
    bucket=cfg('amazon.bucket'),
    directory=cfg('amazon.directory'),
):
    """ Upload file """

    file_type = file.split('.')[-1]
    name = f"{directory}/{generate()}.{file_type}"

    s3client.upload_file(
        file, bucket, name,
        ExtraArgs={'ACL': 'public-read'},
    )

    return LINK + name

def get_policy(bucket=cfg('amazon.bucket')):
    """ Get bucket policy """
    return s3client.get_bucket_policy(Bucket=bucket)


__all__ = (
    's3',
    's3client',
    'ClientError',
    'upload_file',
    'get_policy',
)
