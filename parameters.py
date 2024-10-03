import pathlib
import pymongo
import certifi
import boto3

# mongodb atlas setup
mongo_domain = "mongodb+srv://harsha:harsha@testaccount.euskw.mongodb.net/?retryWrites=true&w=majority&appName=TestAccount"
myclient = pymongo.MongoClient(mongo_domain, tlsCAFile=certifi.where())

mydb = myclient["Microland"]
usersCollection = mydb["Users"]
dataCollection = mydb["Data"]

# "mongodb+srv://harsha:harsha@testaccount.euskw.mongodb.net/?retryWrites=true&w=majority&appName=TestAccount/Microland"