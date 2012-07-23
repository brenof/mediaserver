from psycopg2.pool import SimpleConnectionPool
from flask.ext.login import UserMixin
from uuid import uuid4 as uuid

class User(UserMixin):
    
    def __init__(self, id, email, passw):
        self.id = id
        self.email = email
        self.passw = passw

class Datastore(object):
    """
    the datastore interface
    """
    
    def __init__(self, dbname='web', dbuser='mediaserver', dbpassw='Klofcumad1'):
        self.db = dbname
        self.dbuser = dbuser
        self.dbpassw = dbpassw
        self.pool = SimpleConnectionPool(1, 100, database=dbname, user=dbuser, password=dbpassw)
        
    def start_op(self):
        conn = self.pool.getconn()
        cur = conn.cursor()
        return (conn, cur)
    
    def close_op(self, conn):
        conn.commit()
        self.pool.putconn(conn)        

    def find_user(self, id=None, email=None):        
        assert(id != None or email != None)
        conn, cur = self.start_op()
        if id != None:
            cur.execute("SELECT * FROM users WHERE id=%s", [id])
        if email != None:
            cur.execute("SELECT * FROM users WHERE email=%s", [email])
        row = cur.fetchone()
        print(row)
        if row != None:
            return User(id=row[1], email=row[0], passw=row[2])
        return None
    
    def add_user(self, email, password):
        assert(email != None and password != None)
        conn, cur = self.start_op()
        id = uuid()
        cur.execute("INSERT INTO users (id, email, password) VALUES (%s, %s, %s)", [str(id), email, password])
        self.close_op(conn)
        return id
            
            
     
