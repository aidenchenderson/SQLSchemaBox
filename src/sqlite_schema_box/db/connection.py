import sqlite3


class DB:
    def __init__(self, database=":memory:"):
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = sqlite3.Row


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()


    def commit(self):
        self.conn.commit()


    def rollback(self):
        self.conn.rollback()


    def close(self):
        self.conn.close()