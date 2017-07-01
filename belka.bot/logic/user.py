import os
import sqlite3

from logic.db_controller import DbController
from logic.event import Event


class User:
    def __init__(self, id_, first_name, last_name, phone, chat_id, username, is_staff):
        self._id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.chat_id = chat_id
        self.username = username
        self.is_staff = is_staff
        self.__db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'User')

    @staticmethod
    def registration(first_name, last_name, phone, chat_id, username):
        try:
            db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'User')
            id_ = db.create(first_name=first_name, last_name=last_name, phone=phone,
                            chat_id=chat_id, username=username, is_staff=False)
            return User(id_, first_name, last_name, phone, chat_id, username, False)
        except sqlite3.Error as e:
            print(e)
        return None

    @staticmethod
    def get_user(param_name, param_value):
        try:
            db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'User')
            data = db.get(param_name, param_value)
            if (data == None):
                return None
            is_staff = 'True' is data['is_staff']
            return User(data['id'], data['first_name'], data['last_name'], data['phone'], data['chat_id'], data['username'], is_staff)
        except sqlite3.Error as e:
            print(e)
        return None

    @staticmethod
    def all_user(param_name=None, param_value=None):
        try:
            db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'User')
            users = db.all(param_name, param_value)
            user_list = []
            for data in users:
                is_staff = 'True' is data['is_staff']
                user_list.append(User(data['id'], data['first_name'], data['last_name'], data['phone'], data['chat_id'],
                                 data['username'], is_staff))
            return user_list
        except sqlite3.Error as e:
            print(e)
        return None

    def update(self):
        try:
            self.__db.update(self._id, first_name=self.first_name, last_name=self.last_name, phone=self.phone,
                             chat_id=self.chat_id, username=self.username, is_staff=self.is_staff)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def get_events(self):
        try:
            events = self.__db.query(f'SELECT * from Event JOIN EventToUser ON Event.id = EventToUser.event_id WHERE '
                                     f'EventToUser.user_id={self._id};')
            print(events)
            event_list = []
            for data in events:
                event_list.append(Event(data['id'], data['name'], data['description'], data['photo'], data['date'],
                                        data['time']))
            return event_list
        except sqlite3.Error as e:
            print(e)
            return None

    def accept_event(self, event_id):
        db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'EventToUser')
        try:
            db.create(event_id=event_id, user_id=self._id)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def decline_event(self, event_id):
        db = DbController(os.path.join(os.getcwd(), '..', 'db.sqlite3'), 'EventToUser')
        try:
            db.query(f'DELETE FROM {db.table} WHERE event_id={event_id} and user_id = {self._id};')
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def delete_user(self):
        try:
            self.__db.delete(self._id)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
