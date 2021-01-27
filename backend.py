"""Handles the sqlite3 database."""
import sqlite3
from csv import DictReader as csv_DictReader
from csv import writer as csvwriter
from csv import reader as csvreader
from collections import OrderedDict
from os.path import basename


def create_connection():
    """
    Create a database connection to the SQLite3 database.

    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(r"db\parts.db")
        return conn
    except Exception as e:
        print(repr(e))

    return None


def close_connection(conn):
    """
    Close database connection to the SQLite3 database.

    :param conn: Connection object
    """
    try:
        conn.commit()
        conn.close()
    except Exception as e:
        print(repr(e))


def create_table(create_table_sql):
    """
    Create a table from the create_table_sql statement.

    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    conn = create_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute(create_table_sql)
            close_connection(conn)
            return True
        except Exception as e:
            print(e)
    else:
        print("Error! Unable to establish connection to the database.")


def remove_table(table):
    """
    Remove table from SQLite3 database.

    :param table:  Table to be removed
    """
    conn = create_connection()

    try:
        if conn is not None:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS " + table)
            close_connection(conn)
            return True
        else:
            raise sqlite3.OperationalError
    except sqlite3.OperationalError as e:
        return e


def return_table(table):
    """
    Return table.

    :param table:  Table to be returned
    """
    conn = create_connection()

    cur = conn.cursor()
    sql = "SELECT * FROM " + table
    cur.execute(sql)
    results = cur.fetchall()
    close_connection(conn)

    return results


def return_column_names(table):
    """
    Return all column names from table

    :param table:  Table to pull column names from
    """
    conn = create_connection()

    cur = conn.cursor()
    sql = "SELECT * FROM " + table
    cur.execute(sql)
    names = [description[0] for description in cur.description]
    close_connection(conn)
    return names


def return_possible_values(table, column):
    """
    Return all possible values from a column in table.

    :param table:  Table to search
    :param column:  Column with the values we want
    :return result:  List of values in column
    """
    conn = create_connection()

    cur = conn.cursor()
    values = [value[0] for value in cur.execute("SELECT " + column + " FROM " + table)]
    close_connection(conn)
    result = []
    for value in values:
        if value not in result and value != "":
            result.append(value)

    return sorted(result)


def part_in_db(table, part_num):
    """
    Checks to see if part exists in the database.

    :param conn: Connection object
    :param table: Name of database table
    :param part: Part number to check
    :return: True or False
    """
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT count(*) FROM " + table + " WHERE part_num = ?"
    cur.execute(sql, (part_num,))
    result = cur.fetchone()[0]
    close_connection(conn)
    return result


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

        if part_in_db(table, part):
            cur.execute("SELECT * FROM " + table + " WHERE part_num = ?", (part,))
            result = cur.fetchone()
            close_connection(conn)
            return result
        else:
            return None
    else:
        print("Error! Unable to connect to the database.")


def filter_columns(table, my_dict):
    """
    Selects all records from db table where my_dict[column] = "desired value"

    :param table:  Table we're filtering
    :param my_dcit: Dictionary of columns and desired values
    """
    conn = create_connection()
    sql_fragments = []
    for k, v in my_dict.items():
        sql_fragments.append(k + " = '" + v + "'")

    if conn is not None:
        cur = conn.cursor()
        sql = "SELECT * FROM " + table.lower() + " WHERE " + " AND ".join(sql_fragments)
        cur.execute(sql)
        result = cur.fetchall()
        close_connection(conn)
        return result


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
        if table.startswith("hdd"):
            headers = [
                "part_num PRIMARY KEY",
                "brand",
                "connector",
                "hdd_capacity",
                "ssd_capacity",
                "speed",
                "type",
                "physical_size",
                "height",
                "interface",
                "description",
                "do_not_sub",
                "subbed",
            ]
        if table.startswith("mem"):
            headers = [
                "part_num PRIMARY KEY",
                "speed",
                "brand",
                "connector",
                "capacity",
                "description",
                "do_not_sub",
                "subbed",
            ]
        if table.startswith("cpu"):
            headers = [
                "part_num PRIMARY KEY",
                "brand",
                "description",
                "oem_part_num",
                "do_not_sub",
                "subbed",
            ]
        create_table(
            "CREATE TABLE IF NOT EXISTS " + table + "(" + ",".join(headers) + ");"
        )
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
        if part_in_db(table, part_num):
            cur = conn.cursor()
            cur.execute("SELECT * FROM " + table + ";")
            sql = "DELETE FROM " + table + " WHERE part_num = ?"
            cur.execute(sql, (part_num,))
            close_connection(conn)
            return "Done"
        else:
            return None
    else:
        print("Error! Unable to connect to the database.")


def convert_to_dict(table, part_num):
    """
    Gets row data of part_num from table and
    converts it to a dict.

    :param table: Name of database table
    :param part_num: Part number as string
    :return: Record of part_num
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + table + ";")
        headers = [list[0] for list in cur.description]
        part_info = search_part(table, part_num)
        part_dict = OrderedDict(zip(headers, part_info))
        close_connection(conn)
        return part_dict
    else:
        print("Error! Unable to connect the database.")


def update_part(table, part_info):
    """
    Update part info in database.

    :param table:
    :param part_info:
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + table + ";")
        columns = ["?" for list in cur.description]
        sql = "REPLACE INTO " + table + " VALUES (" + ",".join(columns) + ");"
        cur.execute(sql, part_info)
        close_connection(conn)
        return "Done"
    else:
        print("Error! Unable to connect to the database.")


def list_subs(table, part_num):
    """
    Compares to parts to see if they are valid subs.

    :param table: Name of database table
    :param part_num: Part number as string
    :return: List of subs for part_num
    """
    conn = create_connection()

    def sort_results(results):
        """Places part_num at index 0 of the list"""
        for result in results:
            if part_num in result:
                results.insert(0, results.pop(results.index(result)))
        return results

    if conn is not None:
        cur = conn.cursor()
        part_dict = convert_to_dict(table, part_num)
        if table.startswith("hdd"):
            if part_dict["connector"] == "m.2":
                sql = (
                    "SELECT brand, part_num, type, physical_size, height, \
                       connector, hdd_capacity, ssd_capacity, speed, subbed \
                       FROM "
                    + table
                    + " WHERE (brand = 'CVO' OR brand = ?) \
                       AND type = ? AND physical_size = ? AND connector = ? \
                       AND ssd_capacity = ? AND do_not_sub = 'FALSE' \
                       AND interface like ?"
                )
                values = (
                    part_dict["brand"],
                    part_dict["type"],
                    part_dict["physical_size"],
                    part_dict["connector"],
                    part_dict["ssd_capacity"],
                    part_dict["interface"][:1] + "%",
                )
            else:
                sql = (
                    "SELECT brand, part_num, type, physical_size, height, \
                       connector, hdd_capacity, ssd_capacity, speed, subbed \
                       FROM "
                    + table
                    + " WHERE (brand = 'CVO' OR brand = ?) \
                       AND type = ? AND physical_size = ? AND (height = '' \
                       OR height = ?) AND connector = ? AND hdd_capacity = ? \
                       AND ssd_capacity = ? AND speed = ? \
                       AND do_not_sub = 'FALSE'"
                )
                values = (
                    part_dict["brand"],
                    part_dict["type"],
                    part_dict["physical_size"],
                    part_dict["height"],
                    part_dict["connector"],
                    part_dict["hdd_capacity"],
                    part_dict["ssd_capacity"],
                    part_dict["speed"],
                )
            cur.execute(sql, values)
            # results = [list(filter(None, lst)) for lst in cur.fetchall()]
            results = cur.fetchall()
            return sort_results(results)
        if table.startswith("mem"):
            sql = (
                "SELECT brand, part_num, connector, capacity, speed, subbed \
                   FROM "
                + table
                + " WHERE (brand = 'CVO' OR brand = ?) AND \
                   connector = ? AND capacity = ? AND speed = ? AND \
                   do_not_sub = 'FALSE'"
            )
            cur.execute(
                sql,
                (
                    part_dict["brand"],
                    part_dict["connector"],
                    part_dict["capacity"],
                    part_dict["speed"],
                ),
            )
            results = cur.fetchall()
            return sort_results(results)
        if table.startswith("cpu"):
            sql = (
                "SELECT brand, part_num, oem_part_num, description, subbed \
                   FROM "
                + table
                + " WHERE (brand = 'GPC' or brand = ?) AND \
                    oem_part_num = ? AND do_not_sub = 'FALSE'"
            )
            cur.execute(sql, (part_dict["brand"], part_dict["oem_part_num"]))
            results = cur.fetchall()
        close_connection(conn)
        return sort_results(results)
    else:
        print("Error! Unable to connect to the database.")


def is_valid_sub(table, part_num, other_part_num):
    """
    Calls list_subs and then checks in other_part_num is
    in the list of subs returns.

    :param table: Name of database table
    :param part_num: Part number as string
    :param other_part_num: Part number to check as string
    :return: True or False
    """
    if part_in_db(table, part_num) and part_in_db(table, other_part_num):
        subs = list_subs(table, part_num)
        return any(lst[1] == other_part_num for lst in subs)
    else:
        return False


def import_from_csv(file):
    """
    Import lines from file into SQLite3 database.

    :param file: File to import.
    """
    conn = create_connection()

    if conn is not None:
        table = basename(file).lower()[:-4]
        with open(file, "r") as csvfile:
            reader = csv_DictReader(csvfile)
            first_row = next(reader)
            headers = [header for header, value in first_row.items()]
            headers[0] = "part_num PRIMARY KEY"

            create_table(
                "CREATE TABLE IF NOT EXISTS " + table + "(" + ",".join(headers) + ");"
            )

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
            cur.executemany(
                "INSERT OR IGNORE INTO "
                + table
                + " VALUES ("
                + ",".join(columns)
                + ")",
                to_import,
            )

            close_connection(conn)
    else:
        print("Error! Unable to connect to the database.")


def csv_writer(file, rows):
    """
    Writes rows file

    :param file: File to write to
    :param rows: Row data to write
    """
    with open(file, "w", newline="") as csvfile:
        writer = csvwriter(csvfile)
        writer.writerows(rows)
