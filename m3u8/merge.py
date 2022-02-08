import sys
import os


PATH = '/Users/kosyachniy/Desktop/КурсТТ/8.5/'
PATH_FFMPEG = '/Users/kosyachniy/Desktop/ffmpeg'
PATH_RESULT = '/Users/kosyachniy/Desktop/TikTok/8/5.mp4'
EXCEPTIONS = ['playlist.m3u8']


for file in os.listdir(path=PATH):
    if '.m3u8' in file and file not in EXCEPTIONS:
        header = PATH + file
        break
else:
    sys.exit()

frames = []
with open(header, 'r') as file:
    for row in file:
        if not row or '.ts' not in row or row[0] == '#':
            continue

        frames.append(row.strip().split('?')[0])

print(len(frames))

os.system(
    f"cat {' '.join(PATH + frame for frame in frames)}"
    f" > {PATH}all.ts"
)
os.system(
    f"{PATH_FFMPEG} -i {PATH}all.ts"
    f" -acodec copy -vcodec copy {PATH_RESULT}"
)
