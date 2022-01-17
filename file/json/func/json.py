import json


def from_json(cont):
    return json.loads(cont)

def to_json(cont):
    return json.dumps(cont, ensure_ascii=False, indent='\t')
