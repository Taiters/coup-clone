from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from aiosqlite import Cursor, Row
from typing import AsyncIterator, Generic, TypeVar


TID = TypeVar('TID', int, str)


class MissingAfterCreateException(Exception):
    pass


@dataclass
class TableRow(Generic[TID]):
    id: TID


T = TypeVar('T', bound=TableRow)


class Table(Generic[T, TID], ABC):
    TABLE_NAME = ''
    TABLE_DEFINITION = ''
    COLUMNS: list[str] = []


    @staticmethod
    @abstractmethod
    def row_factory(cursor: Cursor, row: Row) -> T:
        ...


    @asynccontextmanager
    async def wrap_row_factory(self, cursor: Cursor) -> AsyncIterator:
        previous_row_factory = cursor.row_factory
        cursor.row_factory = self.row_factory # type: ignore[assignment]
        yield
        cursor.row_factory = previous_row_factory


    async def get(self, cursor: Cursor, id: TID) -> T:
        select = f'SELECT {", ".join(self.COLUMNS)}'
        from_table = f'FROM {self.TABLE_NAME}'
        where = f'WHERE id = :id'
        query = f'{select} {from_table} {where};'
        async with self.wrap_row_factory(cursor):
            await cursor.execute(query, {
                'id': id
            })
            return await cursor.fetchone() # type: ignore[return-value]
    

    async def query(self, cursor: Cursor, **kwargs: dict) -> list[T]:
        matches = [f'{c} = :{c}' for c in kwargs.keys()]
        select = f'SELECT {", ".join(self.COLUMNS)}'
        from_table = f'FROM {self.TABLE_NAME}'
        where = f'WHERE {" AND ".join(matches)}'
        query = f'{select} {from_table} {where};'
        async with self.wrap_row_factory(cursor):
            await cursor.execute(query, kwargs)
            return await cursor.fetchall() # type: ignore[return-value]
    
    
    async def create(self, cursor: Cursor, **kwargs: dict) -> T:
        columns = list(kwargs.keys())
        value_list = [f':{c}' for c in columns]
        insert = f'INSERT INTO {self.TABLE_NAME} ({", ".join(columns)})'
        values = f'VALUES ({", ".join(value_list)})'
        query = f'{insert} {values};'
        await cursor.execute(query, kwargs)
        await cursor.execute(
            f'SELECT {",".join(self.COLUMNS)} FROM {self.TABLE_NAME} WHERE ROWID = last_insert_rowid()'
        )
        async with self.wrap_row_factory(cursor):
            result = await cursor.fetchone()
        if result is None:
            raise MissingAfterCreateException(
                f'Last inserted row not found for table: {self.TABLE_NAME}'
            )
        return result
    

    async def update(self, cursor: Cursor, id: TID, **kwargs: dict) -> None:
        fields = [f'{f} = :{f}' for f in kwargs.keys()]
        update = f'UPDATE {self.TABLE_NAME}'
        values = f'SET {", ".join(fields)}'
        where = f'WHERE id = :id'
        query = f'{update} {values} {where};'
        await cursor.execute(query, {
            'id': id,
            **kwargs,
        })


    async def delete(self, cursor: Cursor, id: TID) -> None:
        query = f'DELETE FROM {self.TABLE_NAME} WHERE id = :id'
        await cursor.execute(query, {
            'id': id
        })