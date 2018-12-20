import subprocess


file_in = 'test.mp3'
file_out = 'test.ogg'

frommp3 = subprocess.Popen(['data', '-w', '-', 'data/' + file_in], stdout=subprocess.PIPE)
toogg = subprocess.Popen(['oggenc', '-'], stdin=frommp3.stdout, stdout=subprocess.PIPE)

with open('data/' + file_out, 'wb') as outfile:
	while True:
		data = toogg.stdout.read(1024 * 100)
		if not data:
			break

		outfile.write(data)