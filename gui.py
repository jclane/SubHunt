import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from partsDB import *


def import_list():
    """Opens a dialog window to pick file"""
    file = tk.filedialog.askopenfilename(title="Import", filetypes=[("CSV files", "*.csv")])
    
    if file != "":
        add_from_file(file)

            
def blah():
    messagebox.showinfo("Title", show_part("00FC422")) 
    

class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
    
        tk.Tk.__init__(self, *args, **kwargs)
        
        window = tk.Frame(self)
        window.grid(row=0, column=0, padx=10, pady=10)
        
        COMMANDS = ["add", "del", "show", "sub", "list", "import", "purge db", "help"]
        
        add_button = tk.Button(window, text="Import", command=import_list)
        add_button.pack()
                
        delete_me_button = tk.Button(window, text="BLAH", command=blah)
        delete_me_button.pack()
                
        purge_button = tk.Button(window, text="Purge", command=purge)
        purge_button.pack()

if __name__ == "__main__":
    app = Main()
    app.title("partsDB")
    app.mainloop()        
