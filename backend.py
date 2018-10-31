import sqlite3
import csv
from os.path import basename


def create_connection():
    """
    Create a database connection to the SQLite3 database.
    
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(r"db\parts.db")
        return conn
    except Error as e:
        print(e)
        
    return None
    

def close_connection(conn):    
    """
    Close database connection to the SQLite3 database.
    
    :param conn: Connection object
    """
    try:
        conn.commit()
        conn.close()
    except Erro as e:
        print(e)   
    

def part_in_db(conn, table, part_num):
    """
    Checks to see if part exists in the database.
    
    :param conn: Connection object
    :param table: Name of database table
    :param part: Part number to check
    :return: True or False
    """
    cur = conn.cursor()
    sql = "SELECT count(*) FROM " + table + " WHERE part_num = ?"
    cur.execute(sql, (part_num,)) 
    return cur.fetchone()[0]
    
    
def create_table(conn, create_table_sql):
    """
    Create a table from the create_table_sql statement.
    
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        print(e)
            

def add_part(table, part_info):
    """
    Adds part to the SQLite3 database.
    
    :param table: Name of database table
    :param part: part_info to add
    :return: "Done" 
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + table + ";")
        columns = ["?" for list in cur.description]  
        sql = "INSERT OR IGNORE INTO " + table + " VALUES (" + ",".join(columns) + ");"
        cur.execute(sql, part_info)
        close_connection(conn)
        return "Done"
    else:
        print("Error! Unable to connect to the database.")    
    
            
def remove_part(table, part_num):
    """
    Removes a part from the SQLite3 databse.
    
    :param table: Name of database table
    :param part: Part to remove
    :return: "Done" or None
    """
    conn = create_connection()
    if conn is not None:
        if part_in_db(conn, table, part_num):
            cur = conn.cursor()
            sql = "DELETE FROM " + table + " WHERE part_num = ?"
            cur.execute(sql, (part_num,))
            close_connection(conn)
            return "Done"
        else:
            return None
    else:
        print("Error! Unable to connect to the database.")
        
    
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
            first_row = next(reader)
            headers = [header for header,value in first_row.items()]
            headers[0] = "part_num PRIMARY KEY"
            
            create_table(conn, "CREATE TABLE IF NOT EXISTS " + table + "(" + ",".join(headers) + ");")
            
            to_import = [list(row.values()) for row in reader]
            to_import.append(list(first_row.values()))
            
            for list_item in to_import:
                for item in list_item:
                    if item.endswith("\xa0"):
                        index_of_list = to_import.index(list_item)
                        index_of_item = list_item.index(item)
                        to_import[index_of_list][index_of_item] = item.strip()

            cur = conn.cursor()
            columns = ["?" for item in headers]
            cur.executemany("INSERT OR IGNORE INTO " + table + " VALUES (" + ",".join(columns) + ")", to_import)
            
            close_connection(conn)
    else:
        print("Error! Unable to connect to the database.")
    
    
def search_part(table, part):
    """
    Returns part info if part is in database.
    
    :param conn: Connection object
    :param table: Name of database table
    :param part: Part number
    :return: Part info or None
    """
    conn = create_connection()
    
    if conn is not None:
        cur = conn.cursor()
        
        if part_in_db(conn, table, part):
            cur.execute("SELECT * FROM " + table + " WHERE part_num = ?", (part,))
            result = cur.fetchone()
            close_connection(conn)
            return result    
        else:
            return None
    else:
        print("Error! Unable to connect to the database.")        

            
def purge():
    """
    Purge all records from SQLite3 database.
    """
    conn = create_connection()
    
    if conn is not None:
        cur = conn.cursor()
        tables = ["mem"]
        for table in tables:
            cur.execute("DROP TABLE '" + table + "'")
    else:
        print("Error! Unable to connect to the database.")
        
