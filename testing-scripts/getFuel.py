import json

from math import trunc
value = trunc(0.123456*1000)/1000
print(value)
 
# Opening JSON file
f = open('data.json')
 
# returns JSON object as
# a dictionary
data = json.load(f)

fuel = []

for item in data:
    firstVertice = trunc(item['vertices'][0]['x']*1000)/1000
    if (firstVertice == 0.122):
        fuel.append(item)
print(fuel)