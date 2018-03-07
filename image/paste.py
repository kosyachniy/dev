from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

TEMPLATE = 1
IMAGE = 1
TEXT = 'Здесь шрифт FS Joey'

def paste(template, image, text):
	img = Image.open('tpl%d.png' % TEMPLATE, 'r')
	'''

	print(img_w, img_h)
	'''

	background = Image.open('%d.jpg' % IMAGE, 'r')
	'''
	bg_w, bg_h = background.size
	print(bg_w, bg_h)
	'''

	bck2 = Image.new('RGBA', img.size, (255, 255, 255, 255))

	img_w, img_h = img.size
	background = background.resize((int(img_w * 0.9), int(img_h * 0.85)), Image.ANTIALIAS)

	bck2.paste(background, (int(img_w * 0.1), 0))
	bck2.paste(img, (0, 0), img)

	draw = ImageDraw.Draw(bck2)
	font = ImageFont.truetype('FS_JoeyPro.otf', 60)
	draw.text((int(0.15 * img_w), int(0.86 * img_h)), text, (0, 0, 0), font=font)

	bck2.save('out.png')

if __name__ == '__main__':
	paste(TEMPLATE, IMAGE, TEXT)