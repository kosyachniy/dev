from lib.aws import s3, upload_file, get_policy


if __name__ == '__main__':
    for bucket in s3.buckets.all():
        print(bucket.name)
        print(get_policy(bucket.name))

    print(upload_file(input("Файл: ")))
