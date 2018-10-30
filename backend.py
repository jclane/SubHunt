import sqlite3
import csv
from os.path import basename


def create_connection():
    """
    Create a database connection to the SQLite3 database.
    
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect("parts.db")
        return conn
    except Error as e:
        print(e)
        
    return None
    

def close_connection(conn):    
    """Close database connection to the SQLite3 database."""
    try:
        conn.commit()
        conn.close()
    except Erro as e:
        print(e)   
    
    
def create_table(conn, create_table_sql):
    """
    Create a table from the create_table_sql statement.
    
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
            

def import_from_csv(file):
    """
    Import lines from file into SQLite3 database.
    
    :param file: File to import.
    """
    conn = create_connection()
    
    if conn is not None:
        table = basename(file).lower()[:3]
        with open(file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            headers = next(reader)
            
            create_table(conn, "CREATE TABLE IF NOT EXISTS " + table + " (" + ",".join(headers.keys()) + ");")
            
            to_import = [list(row.values()) for row in reader]
            
            for list_item in to_import:
                for item in list_item:
                    if item.endswith("\xa0"):
                        index_of_list = to_import.index(list_item)
                        index_of_item = list_item.index(item)
                        to_import[index_of_list][index_of_item] = item.strip()

            cur = conn.cursor()
            columns = ["?" for item in headers]
            cur.executemany("INSERT INTO " + table + " VALUES (" + ",".join(columns) + ")", to_import)
            
            close_connection(conn)
    else:
        print("Error! Unable to connect to the database.")
     
     
def purge():
    """
    Purge all records from SQLite3 database.
    """
    conn = create_connection()
    cur = conn.cursor()
    tables = ["mem"]
    for table in tables:
        cur.execute("DROP TABLE '" + table + "'")
