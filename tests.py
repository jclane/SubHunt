from backend import *


def import_test():
    """Test import from csv"""
    import_from_csv(r".\import\mem_test.csv")
    import_from_csv(r".\import\hdd_test.csv")
    try:
        assert part_in_db("mem_test", "123") == True
        assert part_in_db("mem_test", "456") == True
        assert part_in_db("mem_test", "789") == True
        assert part_in_db("hdd_test", "1111111") == True
        assert part_in_db("hdd_test", "1111112") == True
        assert part_in_db("hdd_test", "2222222") == True
        assert part_in_db("hdd_test", "2222223") == True
        print("Import: Passed!\n")
    except AssertionError as e:
        print("Import: Failed!\n")
        print(str(e))
        

def add_part_test():
    """Test adding parts to database"""
    part_mem = ["111","PC4-19200S","Lenovo","SO-DIMM","8GB","8GB DDR4 2400 SoDIMM","FALSE","TRUE"]
    part_hdd = ["111","Lenovo","SATA","500","","7200","HDD","2.5","7","SATA III","","FALSE","TRUE"]
    add_part("mem_test", part_mem)
    add_part("hdd_test", part_hdd)
    try:
        assert part_in_db("mem_test", "111") == True
        assert part_in_db("hdd_test", "111") == True
        print("Add part: Passed!\n")
    except AssertionError as e:
        print("Add part:Failed!\n")
        print(str(e))


def remove_part_test():
    """Test removed parts from database"""
    remove_part("mem_test", "111")
    remove_part("hdd_test", "111")
    try:
        assert part_in_db("mem_test", "111") == False
        assert part_in_db("hdd_test", "111") == False
        print("Remove part: Passed!\n")
    except AssertionError as e:
        print("Remove part: Failed!\n")
        print(str(e))

        
def list_subs_test():
    """Test checking listing of subs"""
    part_needing_sub = ["111","Acer","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    sub = ["112","Acer","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    also_a_sub = ["113","CVO","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    not_a_sub = ["222","Acer","SATA","500","","5400","SSHD","2.5","7","SATA III","","TRUE","FALSE"]
    also_not_a_sub = ["223","Acer","SATA","","500","5400","SSD","2.5","7","SATA III","","FALSE","FALSE"]
    
    add_part("hdd_test", part_needing_sub)
    add_part("hdd_test", sub)
    add_part("hdd_test", also_a_sub)
    add_part("hdd_test", not_a_sub)
    add_part("hdd_test", also_not_a_sub)
    subs = list_subs("hdd_test", part_needing_sub[0])
    try:
        assert any(lst[1] == "112" for lst in subs) == True
        assert any(lst[1] == "113" for lst in subs) == True
        assert any(lst[1] == "222" for lst in subs) == False
        assert any(lst[1] == "223" for lst in subs) == False
        print("List subs: Passed!\n")
    except AssertionError as e:
        print("List subs: Failed!\n")
        print(repr(e))

        
def valid_sub_test():
    """Test checking if subs are valid"""
    part_needing_sub = ["111","Acer","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    sub = ["112","Acer","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    also_a_sub = ["113","CVO","SATA","500","1000","5400","SSHD","2.5","7","SATA III","","FALSE","TRUE"]
    not_a_sub = ["222","Acer","SATA","500","","5400","SSHD","2.5","7","SATA III","","TRUE","FALSE"]
    also_not_a_sub = ["223","Acer","SATA","","500","5400","SSD","2.5","7","SATA III","","FALSE","FALSE"]
    
    add_part("hdd_test", part_needing_sub)
    add_part("hdd_test", sub)
    add_part("hdd_test", also_a_sub)
    add_part("hdd_test", not_a_sub)
    add_part("hdd_test", also_not_a_sub)
    try:
        assert is_valid_sub("hdd_test", "111", "112") == True
        assert is_valid_sub("hdd_test", "112", "113") == True
        assert is_valid_sub("hdd_test", "111", "222") == False
        assert is_valid_sub("hdd_test", "113", "223") == False
        assert is_valid_sub("hdd_test", "222", "223") == False
        print("Valid sub: Passed!\n")
    except AssertionError as e:
        print("Valid sub: Failed!\n")
        print(repr(e))        
        

def edit_part_test():
    """Test checking if parts are updated correctly"""
    part_num = ["TEST", "999", "999", "999", "999", "999", "999", "999", "999", "999", "999", "TRUE", "TRUE"]
    update_part_num = ["TEST", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "FALSE", "FALSE"]
    
    add_part("hdd_test", part_num)
    update_part("hdd_test", update_part_num)
    updated_part = [value for key, value in convert_to_dict("hdd_test", "TEST").items()]
    try:
        assert updated_part == update_part_num
        print("Edit part: Passed!\n")
    except AssertionError as e:
        print("Edit part: Failed!\n")
        print(repr(e))
    
    
def remove_table_test():
    """Test checking if tables are removed correctly"""
    try:
        assert remove_table("hdd_test") == True
        assert remove_table("mem_test") == True
        assert remove_table("cpu_test") == True
        print("Remove table: Passed!\n")
    except AssertionError as e:
        print("Remove table: Failed!\n")
        print(repr(e))
     
                
import_test()
add_part_test()
remove_part_test()    
list_subs_test()
valid_sub_test()
edit_part_test()
remove_table_test()
