import re
from sqlite_schema_box.db.executor import Executor
from sqlite_schema_box.db.models import Column, ForeignKey, Schema, Table, UniqueConstraint

class SchemaManager:
    def __init__(self, executor: Executor):
        self.executor = executor


    # protect against injections
    def _validate_name(self, name: str):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"Invalid SQL identifier: '{name}'")


    def _convert_column_to_sql(self, column: Column) -> str:
        self._validate_name(column.name)
        sql = f"{column.name} {column.sql_type}"

        if column.primary_key:
            sql += " PRIMARY KEY"
        if not column.nullable:
            sql += " NOT NULL"
        if column.default is not None:
            sql += f" DEFAULT {column.default}"

        return sql


    def _convert_create_table_to_sql(self, table: Table) -> str:
        self._validate_name(table.name)
        column_definitions = [self._convert_column_to_sql(col) for col in table.columns]

        for fk in table.foreign_keys:
            self._validate_name(fk.column)
            self._validate_name(fk.references_table)
            self._validate_name(fk.references_column)
            
            column_definitions.append(
                f"FOREIGN KEY ({fk.column}) "
                f"REFERENCES {fk.references_table}({fk.references_column})"
            )

        for constraint in table.unique_constraints:
            for col in constraint.columns:
                self._validate_name(col)
                
            column_definitions.append(
                f"UNIQUE ({', '.join(constraint.columns)})"
            )

        columns_sql = ",\n    ".join(column_definitions)
        return f"CREATE TABLE {table.name} (\n    {columns_sql}\n);"


    def create_table(self, table: Table):
        sql = self._convert_create_table_to_sql(table)
        self.executor.execute(sql)


    def drop_table(self, table_name: str):
        self._validate_name(table_name)
        sql = f"DROP TABLE IF EXISTS {table_name};"
        self.executor.execute(sql)


    def get_table_schema(self, table_name: str) -> Table:
        self._validate_name(table_name)

        meta_data_rows = self.executor.fetch_all(f"PRAGMA table_info({table_name});")
        columns = [
            Column(
                name = row["name"],
                sql_type = row["type"],
                nullable = not bool(row["notnull"]),
                primary_key = bool(row["pk"]),
                default = row["dflt_value"]
            )
            for row in meta_data_rows
        ]

        meta_data_fk_rows = self.executor.fetch_all(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = [
            ForeignKey(
                column = row["from"],
                references_table = row["table"],
                references_column = row["to"]
            )
            for row in meta_data_fk_rows
        ]

        return Table(
            name = table_name,
            columns = columns,
            foreign_keys = foreign_keys
        )


    def get_schema(self) -> Schema:
        rows = self.executor.fetch_all("""
            SELECT name
            FROM sqlite_schema
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)

        tables = [self.get_table_schema(row["name"]) for row in rows]
        return Schema(tables = tables)