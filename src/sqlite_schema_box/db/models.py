from dataclasses import dataclass
from dataclasses import field


@dataclass
class ForeignKey:
    column: str
    references_table: str
    references_column: str


@dataclass
class Column:
    name: str
    sql_type: str
    nullable: bool = True
    primary_key: bool = False
    default: str | None = None


@dataclass
class UniqueConstraint:
    columns: list[str]


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory = list)
    foreign_keys: list[ForeignKey] = field(default_factory = list)
    unique_constraints: list[UniqueConstraint] = field(default_factory = list)


@dataclass
class Schema:
    tables: list[Table] = field(default_factory = list)