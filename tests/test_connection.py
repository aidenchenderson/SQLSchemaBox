import pytest
from sqlite_schema_box.db.connection import DB


@pytest.fixture
def db():
    database = DB()
    yield database
    database.close()


def test_connection(db):
    assert db.conn is not None
    assert db.cursor is not None


def test_execute_select(db):
    rows = db.execute("SELECT 1 AS value;")

    assert len(rows) == 1
    assert rows[0]["value"] == 1


def test_create_table(db):
    db.create_table(
        "users",
        [("id", "INTEGER"), ("name", "TEXT")],
    )

    assert "users" in db.list_tables()


def test_create_table_invalid_name(db):
    with pytest.raises(ValueError):
        db.create_table(
            "users;",
            [("id", "INTEGER")],
        )


def test_get_schema(db):
    db.create_table(
        "users",
        [("id", "INTEGER"), ("name", "TEXT")],
    )

    schema = db.get_schema("users")

    assert len(schema) == 2
    assert schema[0]["name"] == "id"
    assert schema[0]["type"] == "INTEGER"
    assert schema[1]["name"] == "name"
    assert schema[1]["type"] == "TEXT"


def test_drop_table(db):
    db.create_table(
        "users",
        [("id", "INTEGER")],
    )

    db.drop_table("users")

    assert "users" not in db.list_tables()


def test_reset(db):
    db.create_table("users", [("id", "INTEGER")])
    db.create_table("posts", [("id", "INTEGER")])

    assert len(db.list_tables()) == 2

    db.reset()

    assert db.list_tables() == []


def test_insert_and_fetch(db):
    db.create_table(
        "users",
        [("id", "INTEGER"), ("name", "TEXT")],
    )

    db.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Alice"),
    )

    rows = db.execute("SELECT * FROM users")

    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["name"] == "Alice"