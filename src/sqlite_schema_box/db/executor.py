import sqlite3
from sqlite_schema_box.db.connection import DB


class Executor:
    def __init__(self, db: DB):
        self.db = db


    def execute(self, sql: str, sql_params: tuple = ()) -> sqlite3.Cursor:
        cursor = self.db.conn.cursor()
        cursor.execute(sql, sql_params)
        return cursor


    def fetch_all(self, sql: str, sql_params: tuple = ()) -> list[sqlite3.Row]:
        return self.execute(sql, sql_params).fetchall()


    def fetch_one(self, sql: str, sql_params: tuple = ()) -> sqlite3.Row | None:
        return self.execute(sql, sql_params).fetchone()