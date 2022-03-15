from pymongo import MongoClient
import pymongo


class MongoParser:
    def __init__(self, db_name, mongo_adress='mongodb://localhost:27017/'):
        client = MongoClient(mongo_adress)
        self.db = client[db_name]
        self.posts: pymongo.collection.Collection = self.db.posts

    @staticmethod
    def dist(value, diff):
        return {
            '$gte': value - diff,
            '$lte': value + diff
        }

    def save(self, id, img_path, rus_descr, eng_descr, img_size, img_hue, resized, hue_array, ready, saved_at):
        self.posts.insert_one({'id': id,
                               'img_path': img_path,
                               'descriptions': {
                                   'ru': rus_descr,
                                   'en': eng_descr,
                               },
                               'size': img_size,
                               'hue': img_hue,
                               'resized_img_path': resized,
                               'hue_array': hue_array,
                               'ready': ready,
                               'saved_at': saved_at,
                               },
                              )

    def all_names_and_descr(self, lang=None):
        description_type = 'ru' if lang == 'rus' else 'en'
        db_response = self.posts.find()
        response = list(db_response)
        pic_names = [obj['img_path'] for obj in response]
        descriptions = [obj['descriptions'][description_type] for obj in response]
        return pic_names, descriptions

    def find_obj_by_hue(self, hue, max_hue_diff):
        response = self.posts.find({
            'hue': self.dist(hue, max_hue_diff)
        })
        return list(response)

    def find_same_obj(self, hue, figsize, max_hue_diff=0.03):
        response = self.posts.find_one({
            'hue': self.dist(hue, max_hue_diff),
            'size': figsize})
        output = list(response) if response else None
        return output

    def find_unready(self):
        response = self.posts.find({
            'ready': False
        })
        return list(response) if response else None

    def add_descr(self, id, rus, eng):
        response = self.posts.update_one(
            {'id': id},
            {
                '$set': {'descriptions.ru': rus, 'descriptions.en': eng, 'ready': True}
            }
        )
        return response

    def find_last_n(self, n):
        response = self.posts.find().sort([('saved_at', -1)]).limit(n)
        return list(response) if response else []

