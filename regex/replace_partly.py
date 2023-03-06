import re


def replace_partly(data):
    elements = re.search(r'<[^>"]*"+([^>"]*)"+[^>]*>([^<]*)</[^>]*>', data)
    elements = (elements.group(1), elements.group(2)) if elements else ('', '')

    text = re.sub(r'<[^>]*>([^<]*)</[^>]*>', r'\1', data)
    data = re.sub(r'(<[^>]*>)[^<]*(</[^>]*>)', r'\1new\2', data)

    return elements, text, data


print(replace_partly('<a href="123">456</a>'))
print(replace_partly('<></>'))
