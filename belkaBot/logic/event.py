import psycopg2
import datetime
from logic.db_controller import DbController
#from logic.user import User


class Event:
    def __init__(self, id_, title, description, photo, date, time, shortdescription):
        self._id = id_
        self.title = title
        self.description = description
        self.shortdescription = shortdescription
        self.photo = photo
        #self.date = datetime(*[int(i) for i in date.split('.')])
        #self.time = datetime.time(*[int(i) for i in time.split(':')])
        self.date = date
        self.time = time
        self.__db = DbController(table='Event')

    @staticmethod
    def create_event(title, description, photo, date, time, shortdescription):
        try:
            db = DbController(table='Event')
            id_ = db.create(name=title, description=description, photo=photo, date=date, time=time, shortdescription=shortdescription)
            return Event(id_, title, description, shortdescription, photo, date, time)
        except psycopg2.Error as e:
            print(e)
        return None

    @staticmethod
    def get_event(param_name, param_value):
        try:
            db = DbController(table='Event')
            data = db.get(param_name, param_value)
            return Event(data['id'], data['name'], data['description'], data['photo'], data['date'], data['time'], data['shortdescription'])
        except psycopg2.Error as e:
            print(e)
        return None

    @staticmethod
    def all_event(hashtag_name=None):
        try:
            db = DbController(table='Event')
            command = 'SELECT * FROM "Event";'
            if hashtag_name:
                command = f'{command[:-1]} JOIN "EventToHashtag" ON "Event"."id" = "EventToHashtag"."event_id" ' \
                          f'WHERE "hashtag_id" = \'{hashtag_name.lower()}\';'
            events = db.query(command)
            event_list = []
            for data in events:
                event_list.append(Event(data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            return event_list
        except psycopg2.Error as e:
            print(e)
        return None

    def update(self):
        try:
            self.__db.update(self._id, name=self.title, description=self.description, photo=self.photo, date=self.date,
                             time=self.time, shortdescription=self.shortdescription)
            return True
        except psycopg2.Error as e:
            print(e)
            return False

    # def get_users(self):
    #     try:
    #         users = self.__db.query(f'SELECT * from User JOIN EventToUser ON User.id = EventToUser.user_id WHERE '
    #                                 f'EventToUser.event_id={self._id};')
    #         user_list = []
    #         for data in users:
    #             is_staff = 'True' is data['is_staff']
    #             user_list.append(User(data['id'], data['first_name'], data['last_name'], data['phone'], data['chat_id'],
    #                                   data['username'], is_staff))
    #         return user_list
    #     except psycopg2.Error as e:
    #         print(e)
    #         return None

    def delete_event(self):
        try:
            self.__db.delete(self._id)
            return True
        except psycopg2.Error as e:
            print(e)
            return False
