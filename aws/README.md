# Amazon AWS
## Начало работы
[Описание](https://aws.amazon.com/ru/serverless/)

[Начало работы с AWS](https://aws.amazon.com/ru/getting-started/),
[AWS SDK Python](https://aws.amazon.com/ru/sdk-for-python/),
[Начало работы с AWS на Python](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

[Создание бессерверного веб-приложения](https://aws.amazon.com/ru/getting-started/serverless-web-app/)

## [Получение ключей](https://stackoverflow.com/questions/21440709/how-do-i-get-aws-access-key-id-for-amazon)
1. Go to: http://aws.amazon.com/
2. Sign Up & create a new account (they'll give you the option for 1 year trial or similar)
3. Open the [AWS Console](https://console.aws.amazon.com/)
4. Click on your username near the top right and select **My Security Credentials**
5. Click on **Users** in the sidebar
6. Click on your username
7. Click on the **Security Credentials** tab
8. Click **Create Access Key**
9. Click **Show User Security Credentials**

## Доступ для загрузки и чтения
1. Permissions / Block public access -> Off
2. Permissions / Bucket policy copy from [` bucket-policy.json `](bucket-policy.json)

``` ~/.aws ``` / ``` ~/.aws/credentials ``` / ``` ~/.aws/config ```

```
[default]
aws_access_key_id = <keyskeyskeys>
aws_secret_access_key = <keyskeyskeys>
region=us-east-1
```

- OR -

``` ./sets.json ```

```
{
    "amazon": {
        "key": "<ACCESS KEY ID>",
        "secret": "<ACCESS SECRET KEY>",
        "bucket": "<BUCKET>",
        "directory": "<DIRECTORY>",
        "region": "eu-central-1"
    }
}
```