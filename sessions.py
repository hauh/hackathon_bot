'''Storing sessions with heroku psycopg'''

import os

import psycopg2
from psycopg2.extras import RealDictCursor

##############################

DB_URL = os.environ['DB_URL']


def with_connection(db_transaction):
	def execute_with_connection(*args, **kwargs):
		try:
			with psycopg2.connect(DB_URL, sslmode='require') as conn:
				with conn.cursor(cursor_factory=RealDictCursor) as cursor:
					return db_transaction(cursor, *args, **kwargs)
		except Exception as err:
			err.args = (
				(db_transaction.__name__,)
				+ tuple(args) + tuple(kwargs.items())
				+ err.args if err.args else ()
			)
			raise
	return execute_with_connection

##############################


@with_connection
def init_db(cursor):
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS sessions (
			name	TEXT PRIMARY KEY,
			session	TEXT
		)
	""")


@with_connection
def save_session(cursor, name, session):
	cursor.execute("""
		INSERT INTO sessions (name, session) VALUES (%s, %s)
		ON CONFLICT (name) DO UPDATE SET session = excluded.session
		""",
		(name, session)
	)


@with_connection
def load_session(cursor, name):
	cursor.execute("SELECT session FROM sessions WHERE name = %s", (name,))
	if result := cursor.fetchone():
		result = result['session']
	return result
