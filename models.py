import inspect

import asyncpg

import settings

db = None


async def create_db():
    global db
    db = await asyncpg.create_pool(settings.DB_URL)


class Base:
    """
    Provides base functionality for database models
    """

    def __init__(self, data):
        for k, v in dict(data).items():
            setattr(self, k, v)

    @classmethod
    async def select(cls, **kwargs):
        query = f'SELECT * FROM {cls.__tablename__}{cls._construct_params(kwargs.keys())}'
        result = await cls._fetch(query, kwargs.values())
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            return None
        return result

    @classmethod
    async def insert(cls, **kwargs):
        value_names = ', '.join(kwargs.keys())
        placeholders = ', '.join([f'${i + 1}' for i in range(len(kwargs.keys()))])
        query = f'INSERT INTO {cls.__tablename__} ({value_names}) VALUES ({placeholders})'
        return await cls._execute(query, kwargs.values())

    async def update(self):
        value_names = [f'{k} = ${i + 1}' for i, k in enumerate(dict(self).keys())]
        query = f'UPDATE {self.__tablename__} SET {", ".join(value_names)} WHERE id = ${len(dict(self).keys()) + 1}'
        values = list(dict(self).values())
        values.append(self.id)
        return await self._execute(query, values)

    async def delete(self):
        query = f'DELETE FROM {self.__tablename__} WHERE id = {self.id}'
        return await self._execute(query, [])

    @staticmethod
    async def _execute(query, values):
        return await db.execute(query, *values)

    @classmethod
    async def _fetch(cls, query, values):
        response = await db.fetch(query, *values)
        return [cls(r) for r in response]

    @staticmethod
    def _construct_params(params):
        params_str = ''
        if len(params):
            params_str += f' WHERE '
            kwargs_count = len(params)
            for i, param in enumerate(params):
                params_str += f'{param} = ${i + 1}'
                kwargs_count -= 1
                if kwargs_count != 0:
                    params_str += ' AND '
        return params_str

    def __iter__(self):
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('__') and not inspect.ismethod(value) and not inspect.isfunction(value):
                yield name, getattr(self, name)

    def __repr__(self):
        repr = f'<{self.__class__.__name__} '
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('__') and not inspect.ismethod(value) and not inspect.isfunction(value):
                repr += f'{name}={value} '
        repr = repr.strip() + '>'
        return repr


class CustomEmote(Base):
    """
    Represents a CustomEmote object in the database

    Properties:
        id           int Database ID
        server_id    int Discord server ID
        name         str Name of Pokemon
        emote_string str Tier of Pokemon
    """

    __tablename__ = 'custom_emotes'

    def __init__(self, data):
        super().__init__(data)
