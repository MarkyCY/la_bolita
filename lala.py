from pymongo import MongoClient
import json

client = MongoClient('localhost', 27017)
db = client.bolita
charada = db.charada

with open('json/charadas.json') as f:
    file_data = json.load(f)

#print(file_data)

charada.insert_many(file_data)