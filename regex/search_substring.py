import re


data = 'cxv<h2><strong>wef</strong></h2></h2>/fgdfg<h2></h2><h2>dfg</h2>'

for i in re.finditer(r'<h2>(.*?)</h2>', data):
    print(re.sub(r'(\<(/?[^>]+)>)', '', i.group(1)))
