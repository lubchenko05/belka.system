import psycopg2
from .db_controller import DbController
from .event import Event

class User:
    def __init__(self, id_, first_name, last_name, phone, chat_id, username, is_staff):
        self._id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.chat_id = chat_id
        self.username = username
        self.is_staff = is_staff
        self.__db = DbController(table='User')

    @staticmethod
    def registration(first_name, last_name, phone, chat_id, username):
        try:
            db = DbController(table='User')
            id_ = db.create(first_name=first_name, last_name=last_name, phone=phone,
                            chat_id=chat_id, username=username, is_staff = 0)
            return User(id_, first_name, last_name, phone, chat_id, username, 0)
        except psycopg2.Error as e:
            print(e)
        return None

    @staticmethod
    def get_user(param_name, param_value):
        try:
            db = DbController(table='User')
            data = db.get(param_name, param_value)
            if (data == None):
                return None
            is_staff = data['is_staff']
            return User(data['id'], data['first_name'], data['last_name'], data['phone'], data['chat_id'], data['username'], is_staff)
        except psycopg2.Error as e:
            print(e)
        return None

    @staticmethod
    def all_user(param_name=None, param_value=None):
        try:
            db = DbController(table='User')
            users = db.all(param_name, param_value)
            user_list = []
            for data in users:
                is_staff = data['is_staff']
                user_list.append(User(data['id'], data['first_name'], data['last_name'], data['phone'], data['chat_id'],
                                 data['username'], is_staff))
            return user_list
        except psycopg2.Error as e:
            print(e)
        return None

    def update(self):
        try:
            self.__db.update(self._id, first_name=self.first_name, last_name=self.last_name, phone=self.phone,
                             chat_id=self.chat_id, username=self.username, is_staff=self.is_staff)
            return True
        except psycopg2.Error as e:
            print(e)
            return False

    def get_events(self):
        try:
            db = DbController(table='User')
            events = db.query(f'SELECT * from "Event" JOIN "EventToUser" ON "Event"."id" = '
                              f'"EventToUser"."event_id" WHERE "EventToUser"."user_id"=\'{self._id}\';')
            #print(events)
            event_list = []
            for data in events:
                event_list.append(Event(data[0], data[1], data[2], data[3], data[4], data[5]))
            return event_list
        except psycopg2.Error as e:
            print(e)
            return None

    def accept_event(self, event_id):
        db = DbController(table='EventToUser')
        try:
            db.create(event_id=event_id, user_id=self._id)
            return True
        except psycopg2.Error as e:
            print(e)
            return False

    def decline_event(self, event_id):
        db = DbController(table='EventToUser')
        try:
            db.query(f'DELETE FROM {db.table} WHERE event_id=\'{event_id}\' and user_id = \'{self._id}\';')
            return True
        except psycopg2.Error as e:
            print(e)
            return False

    def delete_user(self):
        try:
            self.__db.delete(self._id)
            return True
        except psycopg2.Error as e:
            print(e)
            return False
