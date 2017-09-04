import os
import psycopg2

class DbController:
    def __init__(self, table, host=DBHOST, db=DBBASE, username=DBUSER, password=DBPASS, port=DBPORT):
        self.host = host
        self.username = username
        self.password = password
        self.table = table
        self.db = db
        self.port = port

    def all(self, param_name='', param_value=''):
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            command = f'SELECT * FROM "{self.table}";'
            if param_name and param_value:
                command = f'{command[:-1]} WHERE "{param_name}" = {param_value};'
            cur = conn.cursor()
            cur.execute(command)
            results = []
            headers = cur.description;
            for values in cur.fetchall():
                result = {}
                for k, v in zip(headers, values):
                    result[k.name] = v
                results.append(result)
        conn.close()
        return results

    def create(self, **kwargs): 
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            keys = ''
            values = ''
            for k, v in kwargs.items():
                keys += f"\"{k}\", "
                values += f"'{v}', "
            command = f'INSERT INTO "{self.table}" ({keys[:-2]}) VALUES ({values[:-2]});'
            c = conn.cursor()
            c.execute(command)
            result = c.lastrowid
            conn.commit()
        conn.close()
        return result

    def get(self, param_name, param_value):
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM "{self.table}" WHERE "{param_name}"=\'{param_value}\';')
            headers = cur.description
            values = cur.fetchone()
            if (values == None):
                return None
            result={}
            for k,v in zip(headers,values):
                result[k[0]] = v
        conn.close()
        return result

    def update(self, _id, **kwargs):
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            command = f'UPDATE "{self.table}" SET '
            for k, v in kwargs.items():
                command = command + f'"{k}" = \'{v}\', '
            c = conn.cursor()
            c.execute(f'{command[:-2]} WHERE "id" = {_id};')
            conn.commit()
        conn.close()

    def delete(self, _id):
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            conn.cursor().execute(f'DELETE FROM "{self.table}" WHERE "id"=\'{_id}\';')
            conn.commit()
        conn.close()

    def query(self, request):
        with psycopg2.connect(f"dbname='{self.db}' user='{self.username}' host='{self.host}' port='{self.port}' password='{self.password}'") as conn:
            cur = conn.cursor()
            cur.execute(request)
            result = cur.fetchall()
            conn.commit()
        conn.close()
        return result
