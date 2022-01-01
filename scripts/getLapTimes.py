import json

from math import trunc
import sys


# Opening JSON file
f = open(sys.argv[1])

 
# returns JSON object as
# a dictionary
data = json.load(f)

laptimes = []

for item in data["lapTimes"]:
    laptimes.append(item["text"])
# laptimes.sort(key=lambda x: x["startTime"], reverse=False)
print(laptimes)
print(len(laptimes))