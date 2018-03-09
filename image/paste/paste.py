from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

TEMPLATE = 1
IMAGE = '1.jpg'
TEXT = 'Здесь шрифт FS Joey'

def paste(image, text, template=TEMPLATE):
	template = Image.open('tpl%d.png' % TEMPLATE, 'r')
	background = Image.open(image, 'r')
	canvas = Image.new('RGBA', template.size, (255, 255, 255, 255))

	template_w, template_h = template.size

	background = background.resize((int(template_w * 0.9), int(template_h * 0.85)), Image.ANTIALIAS)

	canvas.paste(background, (int(template_w * 0.1), 0))
	canvas.paste(template, (0, 0), template)

	draw = ImageDraw.Draw(canvas)
	font = ImageFont.truetype('FS_JoeyPro-MediumRegular.otf', 60)

	text_w, text_h = draw.textsize(text, font=font)
	draw.text(((1.12 * template_w - text_w) // 2, int(0.87 * template_h)), text, font=font, fill='#ed2c2d')

	canvas.save(image[:-4]+'.png')

if __name__ == '__main__':
	paste(IMAGE, TEXT, TEMPLATE)