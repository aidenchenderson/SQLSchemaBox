import sqlite3
import re

class DB:
    def __init__(self, database=":memory:"):
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()


    def execute(self, sql: str, sql_params: tuple = ()):
        self.cursor.execute(sql, sql_params)

        # only save changes that manipulate the database
        if not self.cursor.description:
            self.conn.commit()
            return None

        return self.cursor.fetchall()


    def create_table(self, table_name: str, columns: list[tuple[str, str]]):
        # validates the table name to protect the SQL query
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
            raise ValueError("Error: Invalid Table Name.")

        # converts column name-type pairs into the create statement body
        cols = ", ".join(
            f"{col_name} {col_type}" for col_name, col_type in columns
        )

        sql = f"CREATE TABLE {table_name} ({cols});"

        self.execute(sql)


    def list_tables(self):
        # sqlite_schema sqlite's metadata table
        rows = self.execute("""
        SELECT name
        FROM sqlite_schema
        WHERE type='table'
        ORDER BY name;
        """)

        return [row["name"] for row in rows]


    def get_schema(self, table_name: str):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
            raise ValueError("Error: Invalid Table Name.")

        # pragma is used to inspect the database,
        # with table_info specifically returning metadata about a table's cols
        rows = self.execute(f"PRAGMA table_info({table_name});")
        return rows


    def drop_table(self, table_name: str):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
            raise ValueError("Error: Invalid Table Name.")

        sql = f"DROP TABLE IF EXISTS {table_name}"
        self.execute(sql)


    def close(self):
        self.conn.close()


    def reset(self):
        for table in self.list_tables():
            self.drop_table(table)