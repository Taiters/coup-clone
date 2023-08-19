from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Generic, TypeVar

from aiosqlite import Cursor, Row

TID = TypeVar("TID", int, str)


class MissingAfterCreateException(Exception):
    pass


@dataclass
class TableRow(Generic[TID]):
    id: TID


T = TypeVar("T", bound=TableRow)


class Table(Generic[T, TID], ABC):
    TABLE_NAME = ""
    TABLE_DEFINITION = ""
    COLUMNS: list[str] = []

    @staticmethod
    @abstractmethod
    def row_factory(cursor: Cursor, row: Row) -> T:
        ...

    @classmethod
    @asynccontextmanager
    async def wrap_row_factory(cls, cursor: Cursor) -> AsyncIterator:
        previous_row_factory = cursor.row_factory
        cursor.row_factory = cls.row_factory  # type: ignore[assignment]
        yield
        cursor.row_factory = previous_row_factory

    @classmethod
    async def get(cls, cursor: Cursor, id: TID) -> T:
        select = f'SELECT {", ".join(cls.COLUMNS)}'
        from_table = f"FROM {cls.TABLE_NAME}"
        where = "WHERE id = :id"
        query = f"{select} {from_table} {where};"
        async with cls.wrap_row_factory(cursor):
            await cursor.execute(query, {"id": id})
            return await cursor.fetchone()  # type: ignore[return-value]

    @classmethod
    async def query(cls, cursor: Cursor, **kwargs: Any) -> list[T]:
        matches = [f"{c} = :{c}" for c in kwargs.keys()]
        select = f'SELECT {", ".join(cls.COLUMNS)}'
        from_table = f"FROM {cls.TABLE_NAME}"
        where = f'WHERE {" AND ".join(matches)}'
        query = f"{select} {from_table} {where};"
        async with cls.wrap_row_factory(cursor):
            await cursor.execute(query, kwargs)
            return await cursor.fetchall()  # type: ignore[return-value]

    @classmethod
    async def create(cls, cursor: Cursor, **kwargs: Any) -> T:
        columns = list(kwargs.keys())
        value_list = [f":{c}" for c in columns]
        insert = f'INSERT INTO {cls.TABLE_NAME} ({", ".join(columns)})'
        values = f'VALUES ({", ".join(value_list)})'
        query = f"{insert} {values};"
        await cursor.execute(query, kwargs)
        await cursor.execute(f'SELECT {",".join(cls.COLUMNS)} FROM {cls.TABLE_NAME} WHERE ROWID = last_insert_rowid()')
        async with cls.wrap_row_factory(cursor):
            result = await cursor.fetchone()
        if result is None:
            raise MissingAfterCreateException(f"Last inserted row not found for table: {cls.TABLE_NAME}")
        return result  # type: ignore[return-value]

    @classmethod
    async def update(cls, cursor: Cursor, id: TID, **kwargs: Any) -> None:
        fields = [f"{f} = :{f}" for f in kwargs.keys()]
        update = f"UPDATE {cls.TABLE_NAME}"
        values = f'SET {", ".join(fields)}'
        where = "WHERE id = :id"
        query = f"{update} {values} {where};"
        await cursor.execute(
            query,
            {
                "id": id,
                **kwargs,
            },
        )

    @classmethod
    async def delete(cls, cursor: Cursor, id: TID) -> None:
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = :id"
        await cursor.execute(query, {"id": id})

    @classmethod
    async def count(cls, cursor: Cursor, **kwargs: Any) -> int:
        matches = [f"{c} = :{c}" for c in kwargs.keys()]
        where = f'WHERE {" AND ".join(matches)}'
        query = f"SELECT COUNT(*) FROM {cls.TABLE_NAME} {where}"
        await cursor.execute(query, kwargs)
        row = await cursor.fetchone()
        if row is None:
            return 0
        return row[0]
