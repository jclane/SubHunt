from backend import *


part = ["111","PC4-19200S","Lenovo","SO-DIMM","8GB","8GB DDR4 2400 SoDIMM","FALSE","TRUE"]        

conn = create_connection()

def test1():
    """Test adding parts to database"""
    add_part("mem", part)
    try:
        assert part_in_db(conn, "mem", "111") == True
        print("Add part: Passed!")
    except AssertionError as e:
        print("Add part:Failed!")
        print(e)

def test2():
    """Test removed parts from database"""
    remove_part("mem", "111")
    try:
        assert part_in_db(conn, "mem", "111") == False
        print("Remove part: Passed!")
    except AssertionError as e:
        print("Remove part: Failed!")
        print(e)
        
def test3():
    """Test import from csv"""
    import_from_csv(r".\import\TEST.csv")
    try:
        assert part_in_db(conn, "test", "123") == True
        assert part_in_db(conn, "test", "456") == True
        assert part_in_db(conn, "test", "789") == True
        remove_part("test", "123")
        remove_part("test", "456")
        remove_part("test", "789")
        assert part_in_db(conn, "test", "123") == False
        assert part_in_db(conn, "test", "456") == False
        assert part_in_db(conn, "test", "789") == False
        print("Import: Passed!")
    except AssertionError as e:
        print("Import: Failed!")
        print(e)


test1()
print("\n")
test2()
print("\n")
test3()    
print("\n")

purge()
print("Database purged\n")

close_connection(conn)
