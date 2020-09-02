from pymongo import MongoClient
from hypernetworks.utils import to_data


def save_hn(hn):
    client = MongoClient('mongodb://localhost:27017/')

    db = client.hypernetworks
    posts = db[hn.name]
    data = {hn.name: to_data(hn)['hypersimplices']}

    result = posts.insert_one(data)
    return result.inserted_id
