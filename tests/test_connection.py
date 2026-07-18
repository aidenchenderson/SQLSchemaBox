import pytest
import sqlite3
from sqlite_schema_box.db.connection import DB
from sqlite_schema_box.db.executor import Executor
from sqlite_schema_box.db.schema import SchemaManager
from sqlite_schema_box.db.models import Table, Column, ForeignKey, UniqueConstraint


@pytest.fixture
def db_conn():
    db = DB(":memory:")
    yield db
    db.close()


@pytest.fixture
def executor(db_conn):
    return Executor(db_conn)


@pytest.fixture
def schema_manager(executor):
    return SchemaManager(executor)


def test_db_context_manager_commit(tmp_path):
    db_path = str(tmp_path / "test_commit.db")
    
    with DB(db_path) as db:
        executor = Executor(db)
        executor.execute("CREATE TABLE test (id INTEGER);")
        executor.execute("INSERT INTO test (id) VALUES (1);")
    
    with DB(db_path) as db2:
        executor2 = Executor(db2)
        row = executor2.fetch_one("SELECT * FROM test;")
        assert row["id"] == 1


def test_db_context_manager_rollback(tmp_path):
    db_path = str(tmp_path / "test_rollback.db")
    
    with DB(db_path) as setup_db:
        executor = Executor(setup_db)
        executor.execute("CREATE TABLE test (id INTEGER);")

    with pytest.raises(ValueError):
        with DB(db_path) as failing_db:
            executor = Executor(failing_db)
            executor.execute("INSERT INTO test (id) VALUES (42);")
            raise ValueError("Simulated crash mid-transaction")

    with DB(db_path) as check_db:
        executor_check = Executor(check_db)
        assert executor_check.fetch_one("SELECT * FROM test;") is None


def test_executor_execute_and_fetch(executor):
    executor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);")
    executor.execute("INSERT INTO users (name) VALUES (?), (?);", ("John", "Jane"))

    rows = executor.fetch_all("SELECT name FROM users ORDER BY name ASC;")
    assert len(rows) == 2
    assert rows[0]["name"] == "Jane"
    assert rows[1]["name"] == "John"

    single_row = executor.fetch_one("SELECT name FROM users WHERE id = ?;", (2,))
    assert single_row is not None
    assert single_row["name"] == "Jane"

    missing_row = executor.fetch_one("SELECT name FROM users WHERE id = 999;")
    assert missing_row is None


def test_create_and_get_table_schema(schema_manager):
    """Verifies table syntax building, generation, and retrieval parsing."""
    users_table = Table(
        name = "users",
        columns = [
            Column(name = "id", sql_type = "INTEGER", primary_key = True, nullable = False),
            Column(name = "username", sql_type = "TEXT", nullable = False),
            Column(name = "status", sql_type = "TEXT", default = "'active'")
        ],
        unique_constraints = [UniqueConstraint(columns = ["username"])]
    )

    schema_manager.create_table(users_table)

    fetched_table = schema_manager.get_table_schema("users")
    
    assert fetched_table.name == "users"
    assert len(fetched_table.columns) == 3
    
    col_map = {col.name: col for col in fetched_table.columns}
    
    assert col_map["id"].primary_key is True
    assert col_map["id"].nullable is False
    
    assert col_map["username"].nullable is False
    
    assert col_map["status"].default == "'active'"


def test_foreign_key_parsing(schema_manager):
    parent = Table(name = "parent", columns = [Column(name = "id", sql_type = "INTEGER", primary_key = True)])
    child = Table(
        name = "child",
        columns = [
            Column(name = "id", sql_type = "INTEGER", primary_key = True),
            Column(name = "parent_id", sql_type = "INTEGER")
        ],
        foreign_keys = [
            ForeignKey(column = "parent_id", references_table = "parent", references_column = "id")
        ]
    )

    schema_manager.create_table(parent)
    schema_manager.create_table(child)

    child_schema = schema_manager.get_table_schema("child")
    assert len(child_schema.foreign_keys) == 1
    
    fk = child_schema.foreign_keys[0]
    assert fk.column == "parent_id"
    assert fk.references_table == "parent"
    assert fk.references_column == "id"


def test_get_entire_schema_excludes_internal_tables(schema_manager):
    table_a = Table(name = "alpha", columns = [Column(name = "id", sql_type = "INTEGER")])
    table_b = Table(name = "beta", columns = [Column(name = "id", sql_type = "INTEGER")])
    
    schema_manager.create_table(table_a)
    schema_manager.create_table(table_b)

    schema_manager.executor.execute(
        "CREATE TABLE auto_inc (id INTEGER PRIMARY KEY AUTOINCREMENT, val TEXT);"
    )

    entire_schema = schema_manager.get_schema()
    table_names = [t.name for t in entire_schema.tables]

    assert "alpha" in table_names
    assert "beta" in table_names
    assert "auto_inc" in table_names
    assert "sqlite_sequence" not in table_names


def test_drop_table(schema_manager):
    temp_table = Table(name = "transient", columns = [Column(name = "id", sql_type = "INTEGER")])
    schema_manager.create_table(temp_table)
    
    assert len(schema_manager.get_schema().tables) == 1
    
    schema_manager.drop_table("transient")
    assert len(schema_manager.get_schema().tables) == 0


@pytest.mark.parametrize("malicious_name", [
    "drop table users;", 
    "users;--", 
    "table name with spaces", 
    "system_user(id)"
])
def test_sql_injection_protection(schema_manager, malicious_name):
    with pytest.raises(ValueError, match = "Invalid SQL identifier"):
        schema_manager.drop_table(malicious_name)

    bad_table = Table(name = malicious_name, columns = [Column(name = "id", sql_type = "INTEGER")])
    with pytest.raises(ValueError, match = "Invalid SQL identifier"):
        schema_manager.create_table(bad_table)

    bad_col_table = Table(name = "valid_name", columns = [Column(name = malicious_name, sql_type = "INTEGER")])
    with pytest.raises(ValueError, match = "Invalid SQL identifier"):
        schema_manager.create_table(bad_col_table)