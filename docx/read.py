from docx import Document


doc = Document('1.docx')

text  = []
style = []
for x in doc.paragraphs:
    if x.text != '':
        print(x.style.name, x.text)

# for e in document.element.getiterator():
#     # print(e.tag)
#     print(e.text)
