from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

all_databases = client.list_database_names()
print(all_databases)