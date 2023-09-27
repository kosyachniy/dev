from lib.s3 import upload_file, get_buckets


if __name__ == '__main__':
    for bucket in get_buckets():
        print(bucket)

    print(upload_file(input("Файл: ")))
