"""
Functionality of S3
"""

import os.path
from urllib.parse import urlparse
from io import BytesIO

import requests
import boto3
from botocore.exceptions import NoCredentialsError
from mimetypes import guess_extension
from libdev.cfg import cfg
from libdev.gen import generate


s3 = boto3.client(
    's3',
    endpoint_url=cfg('s3.host'),
    aws_access_key_id=cfg('s3.user'),
    aws_secret_access_key=cfg('s3.pass'),
    region_name='us-east-1',
)


def upload_file(
    file,
    directory=cfg('mode'),
    bucket=cfg('project_name'),
):
    """ Upload file """

    parsed_url = urlparse(file)
    name = f"{directory}/{generate()}"

    try:
        if parsed_url.netloc:
            response = requests.get(file)

            file_type = os.path.splitext(parsed_url.path)[1]
            if not file_type:
                content_type = response.headers.get('Content-Type')
                file_type = guess_extension(content_type.split(';')[0])
            if file_type:
                name += file_type

            file_stream = BytesIO(response.content)
            s3.upload_fileobj(file_stream, bucket, name)

        else:
            file_type = os.path.splitext(file)[1]
            if file_type:
                name += file_type

            s3.upload_file(file, bucket, name)

    except FileNotFoundError:
        return None
    except NoCredentialsError:
        return None

    return f"{cfg('s3.host')}{bucket}/{name}"

def get_buckets():
    """ Get list of buckets """
    return [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]


__all__ = (
    's3',
    'upload_file',
    'get_buckets',
)
