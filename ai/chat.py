from libdev.cfg import cfg
import openai


openai.api_key = cfg('openai_token')


def get(data, messages=None):
    if messages is None:
        messages = []
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages + [{"role": "user", "content": data}],
    ).choices[0].message.content

def main():
    messages = []
    while True:
        req = input("Request: ")
        res = get(req, messages)
        print(res)
        messages.append({"role": "user", "content": req})
        messages.append({"role": "assistant", "content": res})


if __name__ == '__main__':
    # print(get(input("Request: ")))
    main()
