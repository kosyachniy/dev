from dicttoxml import dicttoxml

from xml.dom.minidom import parseString


def from_xml(obj):
	pass

def to_xml(obj):
	res = dicttoxml(obj, attr_type=False).decode('utf-8')
	return parseString(res).toprettyxml()