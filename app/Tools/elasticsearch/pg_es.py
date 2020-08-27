import json

#create metadata lambda function
metadata = lambda id: '{"index":{"_index":"ClothDB","_type":"item","_id":"%s"}'%id

filename = 'es_pre.json'

with open(filename) as f:
    data = json.load(f)

for line in data:
    print(metadata(line["id"]))
    print(str(line).rstrip("\n"))


