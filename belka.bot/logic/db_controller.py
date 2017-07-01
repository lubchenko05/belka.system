import sqlite3
import os


class DbController:
    def __init__(self, db, table_name):
        self.db = db
        self.table = table_name

    def all(self, param_name, param_value):
        with sqlite3.connect(self.db) as conn:
            command = f'SELECT * FROM {self.table};'
            if param_name and param_value:
                command = f'{command[:-2]} WHERE {param_name} = {param_value};'
            c = conn.cursor().execute(command)
            headers = c.description
            results = []
            for values in c.fetchall():
                result = {}
                for k, v in zip(headers, values):
                    result[k[0]] = v
                results.append(result)
        conn.close()
        return results

    def create(self, **kwargs):
        with sqlite3.connect(self.db) as conn:
            keys = ''
            values = ''
            for k, v in kwargs.items():
                keys += f'{k}, '
                values += f'"{v}", '
            command = f'INSERT INTO {self.table} ({keys[:-2]}) VALUES ({values[:-2]});'
            c = conn.cursor()
            c.execute(command)
            result = c.lastrowid
            conn.commit()
        conn.close()
        return result

    def get(self, param_name, param_value):
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor().execute(f'SELECT * FROM {self.table} WHERE {param_name}={param_value};')
            headers = c.description
            values = c.fetchone()
            if (values == None):
                return None
            result={}
            for k,v in zip(headers,values):
                result[k[0]] = v
        conn.close()
        return result

    def update(self, _id, **kwargs):
        with sqlite3.connect(self.db) as conn:
            command = f'UPDATE {self.table} SET '
            for k, v in kwargs.items():
                command = command + f'{k} = "{v}", '
            c = conn.cursor()
            c.execute(f'{command[:-2]} WHERE id = {_id};')
            conn.commit()
        conn.close()

    def delete(self, _id):
        with sqlite3.connect(self.db) as conn:
            conn.cursor().execute(f'DELETE FROM {self.table} WHERE id={_id};')
            conn.commit()
        conn.close()

    def query(self, request):
        with sqlite3.connect(self.db) as conn:
            result = conn.cursor().execute(request).fetchall()
            conn.commit()
        conn.close()
        return result
