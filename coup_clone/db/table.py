from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from sqlite3 import Cursor, Row
from typing import Generic, TypeVar


TID = TypeVar('TID', int, str)


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
        pass


    @asynccontextmanager
    async def wrap_row_factory(self, cursor: Cursor) -> None:
        previous_row_factory = cursor.row_factory
        cursor.row_factory = self.row_factory
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
            return await cursor.fetchone()
    

    async def query(self, cursor: Cursor, **kwargs) -> list[T]:
        matches = [f'{c} = :{c}' for c in kwargs.keys()]
        select = f'SELECT {", ".join(self.COLUMNS)}'
        from_table = f'FROM {self.TABLE_NAME}'
        where = f'WHERE {" AND ".join(matches)}'
        query = f'{select} {from_table} {where};'
        async with self.wrap_row_factory(cursor):
            await cursor.execute(query, {
                'id': id
            })
            return await cursor.fetchall()
    
    
    async def create(self, cursor: Cursor, **kwargs: dict) -> TID:
        columns = list(kwargs.keys())
        values = [f':{c}' for c in columns]
        insert = f'INSERT INTO {self.TABLE_NAME} ({", ".join(columns)})'
        values = f'VALUES ({", ".join(values)})'
        query = f'{insert} {values};'
        await cursor.execute(query, kwargs)
        await cursor.execute(
            f'SELECT id FROM {self.TABLE_NAME} WHERE ROWID = last_insert_rowid()'
        )
        row = await cursor.fetchone()
        return row[0]
    

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