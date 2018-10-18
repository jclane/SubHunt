import shelve
import csv
from itertools import zip_longest
from os.path import basename

from classes import *


def add_part(part, data):
    """
    Adds a part to the database.
    
    :param part: Part number as a string.
    :param data: Object with all relevant part data. 
    """
    
    with shelve.open("partsdb") as db:
        db[part] = data


def add_from_file(file):
    """
    Adds all parts listed in a .CSV file.
    
    :param file: Filename to pull parts from as string.
    """
   
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:

            if row["do_not_sub"] == "TRUE":
                row["do_not_sub"] = True
            elif row["do_not_sub"] == "FALSE":
                row["do_not_sub"] = False
                
            if row["subbed"] == "TRUE":
                row["subbed"] = True
            elif row["subbed"] == "FALSE":
                row["subbed"] = False
            
            if basename(file) == "MEM.csv":
                add_part(row["part_num"], Memory(row["part_num"], row["speed"],
                                                row["brand"], row["connector"], 
                                                row["capacity"], row["description"], 
                                                row["do_not_sub"], row["subbed"]))
            elif basename(file) == "HDD.csv":
                if row["type"] == "SSD":                  
                    add_part(row["part_num"], SolidStateDrive(row["part_num"], row["brand"], 
                                                        row["description"], row["connector"], 
                                                        row["ssd_capacity"], row["physical_size"], 
                                                        row["interface"], row["do_not_sub"], 
                                                        row["subbed"]))
                elif row["type"] == "SSHD":
                    add_part(row["part_num"], HybridDrive(row["part_num"], row["brand"], 
                                                    row["description"], row["connector"], 
                                                    row["hdd_capacity"], row["ssd_capacity"],
                                                    row["speed"], row["physical_size"], 
                                                    row["height"], row["interface"], 
                                                    row["do_not_sub"], row["subbed"]))
                else:
                    add_part(row["part_num"], Harddrive(row["part_num"], row["brand"], 
                                                    row["description"], row["connector"], 
                                                    row["hdd_capacity"], row["speed"], 
                                                    row["physical_size"], row["height"], 
                                                    row["interface"], row["do_not_sub"], 
                                                    row["subbed"]))                
            elif basename(file) == "CPU.csv":
                pass
                               
  
def delete_part(part):
    """
    Deletes a part from the database.
    
    :param part: Part number to be removed as string.
    """
    
    try:
        with shelve.open("partsdb") as db:
            del db[part]
    except KeyError:
        print(part, "does not exist in the database.")
     
     
def show_part(part):
    """
    Pretty prints a part record from the database.
    
    :param part:  Part number to be printed as a string.
    """
    
    try:
        with shelve.open("partsdb") as db:
            return db[part]
    except KeyError:
        print(part, "does not exist in the database.")
        
        
def can_sub(part, other):
    """
    Compares two parts to see if they are 
    valid subs for each other.
    
    :param part: Part number to compare as string.
    :param other: Part number to compare as string.
    :return: Boolean
    """
    
    try:
        with shelve.open("partsdb") as db:
            if db[part].do_not_sub == True:
                return False
            else:
                return db[part] == db[other]
    except KeyError:
        print("One of the provided part numbers does not exist in the database.")        

        
def list_subs(part):
    """
    List all subs for a given part.
    
    :param part: Part number as a string to find
        subs for.
    """
    
    subs = [["Part #", "Capacity", "Speed", "Connector"]]
    
    with shelve.open("partsdb") as db:
        for record in db:
            if type(db[record]) == type(db[part]) and can_sub(part, record):
                subs.append([record, db[record].capacity, db[record].speed, db[record].connector])
    
    widths = [max(len(s) for s in x) for x in zip_longest(*subs, fillvalue="")]
    
    for sub in subs:
        print("".join(word.ljust(w + 2) for word, w in zip(sub, widths)))
        
    
def purge():
    """Removes all parts from the database."""
    
    with shelve.open("partsdb") as db:
        for record in db:
            del db[record]

'''
while True:
    COMMANDS = ["add", "del", "show", "sub", "list", "import", "purge db", "help"]
    
    command = ""
    
    while command not in COMMANDS:
        command, target = input(">> ").split(" ")
    
    if command.lower() == "add":
        # Need to do: Method for inputting part data.
        add_part(target, data)
    elif command.lower() == "del":
        delete_part(target)
    elif command.lower() == "show":
        show_part(target)
    elif command.lower() == "sub":
        other_part = ""
        while other_part == "":
            other_part = input("Part to check? >> ")        
        print(can_sub(target, other_part))
    elif command.lower() == "list":
        list_subs(target)
    elif command.lower() == "import":
        while target not in ["MEM.csv", "CPU.csv", "HDD.csv"]:
            target = input("Please choose from MEM, CPU, or HDD. >> ")
        add_from_file(target)
    elif command.lower() == "purge":
        purge()
'''        
