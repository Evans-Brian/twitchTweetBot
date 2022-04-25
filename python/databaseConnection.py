import psycopg2 as pg2


conn = pg2.connect(database = 'twitch', user = 'postgres', password = '0Gerkins')

cur = conn.cursor()

cur.execute('''CREATE TABLE accounts (
	user_id serial PRIMARY KEY,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	password VARCHAR ( 50 ) NOT NULL,
	email VARCHAR ( 255 ) UNIQUE NOT NULL,
	created_on TIMESTAMP NOT NULL,
        last_login TIMESTAMP 
);''')


cur.execute('''
            select * from accounts;''')