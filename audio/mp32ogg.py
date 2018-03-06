'''
import subprocess

in_file = 'test.mp3'
out_file = 'test.ogg'

frommp3 = subprocess.Popen(['mpg123', '-w', '-', in_file], stdout=subprocess.PIPE)
toogg = subprocess.Popen(['oggenc', '-'], stdin=frommp3.stdout, stdout=subprocess.PIPE)

with open(out_file, 'wb') as outfile:
	while True:
		data = toogg.stdout.read(1024 * 100)
		if not data:
			break
		outfile.write(data)
'''

#!/usr/bin/env python
import subprocess
frommp3 = subprocess.Popen(['data', '-w', '-', '/Users/kosyachniy/Re/project/dev/audio/data/test.mp3'], stdout=subprocess.PIPE)
toogg = subprocess.Popen(['oggenc', '-'], stdin=frommp3.stdout, stdout=subprocess.PIPE)
with open('/tmp/test.ogg', 'wb') as outfile:
    while True:
        data = toogg.stdout.read(1024 * 100)
        if not data:
            break
        outfile.write(data)