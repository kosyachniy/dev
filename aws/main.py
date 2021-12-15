import boto3
from botocore.exceptions import ClientError
from libdev.cfg import cfg
from libdev.gen import generate


LINK = f"https://{cfg('amazon.bucket')}.s3.eu-central-1.amazonaws.com/"


s3 = boto3.resource(
    's3',
    region_name=cfg('amazon.region'),
    aws_access_key_id=cfg('amazon.key'),
    aws_secret_access_key=cfg('amazon.secret'),
)
s3client = s3.meta.client


def upload_file(file, bucket, directory):
    file_type = file.split('.')[-1]
    name = f"{directory}/{generate()}.{file_type}"

    try:
        s3client.upload_file(
            file, bucket, name,
            ExtraArgs={'ACL': 'public-read'},
        )
    except ClientError as e:
        print(e)
        return None

    return LINK + name


if __name__ == '__main__':
    for bucket in s3.buckets.all():
        print(bucket.name)
        print(s3client.get_bucket_policy(Bucket=bucket.name))

    file = input("Файл: ")
    print(upload_file(file, cfg('amazon.bucket'), cfg('amazon.directory')))
