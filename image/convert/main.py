from PIL import Image


NAME = '1.png'


image = Image.open(NAME)
image = image.convert('RGB')
image.save(f"{NAME.split('.')[0]}.webp", 'webp')
