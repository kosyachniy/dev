import subprocess
import re


def convert(folder, source, timeout=None):
    args = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', folder, source]

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    return filename.group(1)


print(convert('./', '1.docx'))
