from pymongo import MongoClient

from hypernetworks.utils.HTInOut import to_data


def load_Hn_into_mongo(hn):
    client = MongoClient('mongodb://localhost:27017/')

    db = client.hypernetworks
    posts = db[hn.name]
    data = {hn.name: to_data(hn)['hypersimplices']}

    result = posts.insert_one(data)
    return result.inserted_id
