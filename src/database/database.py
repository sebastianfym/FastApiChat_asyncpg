import asyncio

import asyncpg
from psycopg2 import Error
from sqlalchemy.orm import declarative_base

from src.config.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
import logging


logging.basicConfig(level=logging.INFO)
Base = declarative_base()


async def create_database():
    try:
        connection = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )

        await connection.execute('''
            CREATE DATABASE postgres;
        ''')

        await connection.close()
        logging.info("База данных успешно создана")

    except (asyncpg.PostgresError, Exception) as e:
        logging.error(f"Ошибка при создании базы данных: {e}")


async def create_table(stmt):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        await connection.execute(stmt)
        logging.info("Таблица успешно создана")
    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL: ", error)
    finally:
        await connection.close()


async def get_all_tables_from_db():
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        query = """
                    SELECT *
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE';
                """
        result = await connection.fetch(query)

        tables = [row['table_name'] for row in result]
        logging.info("Все таблицы в бд: ",tables)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL: ", error)
    finally:
        await connection.close()


async def check_user_in_db(username):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
                    SELECT id FROM users WHERE username = $1;
                """
        user_record = await connection.fetchrow(stmt, username)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL", error)
        user_record = None

    finally:
        connection.close()
        return user_record


async def add_user(username, password):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
                    INSERT INTO users (username, password)
                    VALUES ($1, $2)
                    RETURNING id;
                """
        user_id = await connection.fetchval(stmt, username, password)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL", error)
        user_id = None

    finally:
        connection.close()
        return user_id


async def get_user(username):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
                    SELECT * FROM users WHERE username = $1;
                """
        user = await connection.fetchrow(stmt, username)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL", error, "строка 143")
        user = None
    finally:
        connection.close()
        return user


async def add_messages(sender_id: int, receiver_id: int, message: str):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES ($1, $2, $3)
            RETURNING id, sender_id, receiver_id, message;
        """
        result = await connection.fetchrow(stmt, sender_id, receiver_id, message)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL:", error)
        result = None
    finally:
        await connection.close()
        return result



async def get_last_messages_from_db(user_id: int):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
            SELECT messages.id, messages.sender_id, messages.receiver_id, messages.message
            FROM messages
            WHERE messages.sender_id = $1 OR messages.receiver_id = $1
            ORDER BY messages.id DESC
            LIMIT 20;
        """
        messages = await connection.fetch(stmt, user_id)
        connection.close()
        return [dict(record) for record in messages]

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL:", error)
        connection.close()


async def delete_user_by_username(username: str):
    connection = await asyncpg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        stmt = """
            DELETE FROM users
            WHERE username = $1;
        """
        await connection.execute(stmt, username)

    except (Exception, Error) as error:
        logging.info("Ошибка при работе с PostgreSQL:", error)
    finally:
        await connection.close()


stmt_user_table_create =  """ 
            CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR
            );
        """

stmt_message_table_create = """
    CREATE TABLE messages (
        id SERIAL PRIMARY KEY,
        sender_id INT,
        receiver_id INT,
        message VARCHAR,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    );
"""

