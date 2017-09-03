import psycopg2
from logic.db_controller import DbController

class Hashtag:
    def __init__(self, name):
        self.name = name
        self.__db = DbController(table='Event')

    @staticmethod
    def create_hashtag(name):
        try:
            db = DbController(table='Event')
            db.create(name=name)
            return Hashtag(name)
        except sqlite3.Error as e:
            print(e)
        return None

    @staticmethod
    def get_hashtag(name):
        try:
            db = DbController(table='Event')
            data = db.get('name', name)
            return Hashtag(name)
        except sqlite3.Error as e:
            print(e)
        return None

    @staticmethod
    def all_hashtag():
        try:
            db = DbController(table='User')
            hashtags = db.all()
            hashtag_list = []
            for data in hashtags:
                hashtag_list.append(Hashtag(data['name']))
            return hashtag_list
        except sqlite3.Error as e:
            print(e)
        return None

    def delete_event(self):
        try:
            self.__db.delete(self.name)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
