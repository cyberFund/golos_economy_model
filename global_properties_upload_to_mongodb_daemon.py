#!/usr/bin/python3
from pistonapi.steemnoderpc import SteemNodeRPC
from pymongo import MongoClient
from pprint import pprint
import time
from datetime import datetime

rpc = SteemNodeRPC("wss://ws.golos.io", apis=["follow", "database"])

client = MongoClient("localhost:27017")
database = client["steemdb_1"]
collection_global_properties = database["global_properties"]

sleep_time = 3600

while True:
    global_properties = rpc.get_dynamic_global_properties()
    datetime_now = datetime.now()
    _id = str(datetime_now)
    global_properties.update({
        '_id': _id,
        '_ts': datetime_now
    })
    database.global_properties.update({'_id': _id}, global_properties, upsert=True)
    pprint('Upload Global Properties in MongoDB: {}'.format(_id))
    time.sleep(sleep_time)
