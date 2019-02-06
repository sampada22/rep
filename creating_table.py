import sqlite3
from sqlite3 import Error
import serial
import time
def create_connection(db_file):
	"""create  connection to the SQLite database specified by db_file
	:param db_file:database file
	:return: Connection object or None
	"""

	try:
		conn = sqlite3.connect(db_file)
		print(sqlite3.version)
		return conn
	except Error as e:
		print(e)
	return None

def create_table(conn,create_table_sql):
	"""create a table from the create_table_sql statement
	:param conn :connection object
	:param create_table_sql: a CREATE TABLE statement
	:return:
	"""
	
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def main():
	database = "forecast.db"
	
	sql_create_DHT_logger = """CREATE TABLE IF NOT EXISTS DHT_Data(
	    id integer PRIMARY KEY,
	    humidity text NOT NULL,
	    temp_in_C text NOT NULL,
	    temp_in_F text NOT NULL,
	    heatIndex_in_C NOT NULL,
	    heatIndex_in_F NOT NULL
	);"""
	
	#create a database connection
	conn = create_connection(database)
	if conn is not None:
		#create DHT_logger table
		create_table(conn,sql_create_DHT_logger)
	else:
		print("Error!Cannot create the database conneciton")

if __name__ =='__main__':
	main()


