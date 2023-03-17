import io

import requests
from PIL import Image
from libdev.aws import upload_file

from models.post import Post
from models.user import User


def convert_webp(url):
    image = requests.get(url, stream=True).raw
    image = Image.open(image)
    image = image.convert('RGB')
    data = io.BytesIO()
    image.save(data, format='webp')
    return upload_file(data.getvalue(), file_type='webp')

def main():
    for post in Post.get()[::-1]:
        if not post.image:
            continue

        post.image = convert_webp(post.image)
        post.save()

        print(f"✅ Post #{post.id}")

    for user in User.get()[::-1]:
        if not user.image:
            continue

        user.image = convert_webp(user.image)
        user.save()

        print(f"✅ User #{user.id}")


if __name__ == '__main__':
    main()
