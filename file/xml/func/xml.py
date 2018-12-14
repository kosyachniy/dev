import dicttoxml, xmltodict

from xml.dom.minidom import parseString


def from_xml(obj):
	return xmltodict.parse(obj)['root']

def to_xml(obj):
	res = dicttoxml.dicttoxml(obj, attr_type=False).decode('utf-8')
	return parseString(res).toprettyxml()