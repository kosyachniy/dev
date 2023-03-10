from libdev.cfg import cfg
import openai


openai.api_key = cfg('openai_token')


def get(data):
    response = openai.Image.create(
        prompt=data,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

def main():
    while True:
        req = input("Request: ")
        if not req:
            continue
        res = get(req)
        print("Response:", res, sep="\n")


if __name__ == '__main__':
    main()
