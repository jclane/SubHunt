import shelve
import csv
from itertools import zip_longest

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
        reader = csv.reader(csvfile)
        
        for row in reader:
            part_num = row[0]
            speed = row[1]
            brand = row[2]
            connector = row[3]
            capacity = row[4]
            description = row[5]
            do_not_sub = row[6]
            subbed = row[7]
            
            if do_not_sub == "TRUE":
                do_not_sub = True
            elif do_not_sub == "FALSE":
                do_not_sub = False
                
            if subbed == "TRUE":
                subbed = True
            elif subbed == "FALSE":
                subbed = False
            
            if file == "MEM.csv":
                add_part(part_num, Memory(part_num, speed, brand, connector, capacity, description, do_not_sub, subbed))
            elif file == "HDD.csv":
                pass
            elif file == "CPU.csv":
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
            print(db[part])
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
