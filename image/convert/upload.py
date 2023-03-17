import io

from PIL import Image
from libdev.aws import upload_file


NAME = '1.png'


image = Image.open(NAME)
image = image.convert('RGB')
data = io.BytesIO()
image.save(data, format='webp')
data = data.getvalue()

url = upload_file(data, file_type='webp')
print(url)
