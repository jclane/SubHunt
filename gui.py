from partsDB import *

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

        
def import_list():
    """Opens a dialog window to pick file"""

    file = tk.filedialog.askopenfilename(title="Import", filetypes=[("CSV files", "*.csv")])
    
    if file != "":
        add_from_file(file)
           

class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
    
        tk.Tk.__init__(self, *args, **kwargs)
               
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Import", command=import_list)
        file_menu.add_command(label="Purge Records", command=purge)
        menu.add_cascade(label="File", menu=file_menu)

        edit = tk.Menu(menu, tearoff=False)
        edit.add_command(label="Add")
        edit.add_command(label="Remove")
        edit.add_command(label="Edit")
        menu.add_cascade(label="Edit", menu=edit)

        search_menu = tk.Menu(menu, tearoff=False)
        search_menu.add_command(label="Part Info", command=lambda: self.show_frame("SearchPage"))
        search_menu.add_command(label="Verify Sub")
        search_menu.add_command(label="List Subs", command=lambda: self.show_frame("FindSubsPage"))
        menu.add_cascade(label="Search", menu=search_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Help")
        help_menu.add_command(label="About partDB")
        menu.add_cascade(label="?", menu=help_menu)
        
        self.config(menu=menu)

        container = tk.Frame(self)
        container.grid(column = 0, row = 0, sticky = "NSEW")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (MainPage, SearchPage, FindSubsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()  
    

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller        
        
      
class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Part Info"
        
        def part_info():
            part_num = info_search_box.get()
            
            if part_num != "" and part_in_db(part_num):
                part_info = show_part(part_num).__dict__
                num = 1
                for key in part_info:
                    tk.Label(self, text = key).grid(column = 0, row = num)
                    if key != "do_not_sub" and key != "subbed":
                        tk.Label(self, text = part_info[key]).grid(column = 1, row = num)
                    elif key == "do_not_sub" or key == "subbed":
                        tk.Checkbutton(self, variable = int(part_info[key])).grid(column = 1, row = num)
                        tk.Label(self, text = part_info[key]).grid(column = 2, row = num)
                    
                    num += 1
                  
        
        info_search_label = tk.Label(self, text = "Enter Part Number")
        info_search_label.grid(column = 0, row = 0)
        
        info_search_box = tk.Entry(self, text="")
        info_search_box.grid(column = 1, row = 0)
        
        info_search_button = tk.Button(self, text="Search", command=part_info)
        info_search_button.grid(column = 2, row = 0)
        

class FindSubsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Subs"
        
        def find_subs():
            """Opens a dialog window asking for a part number"""
            part_num = subs_search_box.get()
            
            if part_num != "" and part_in_db(part_num):
                subs = list_subs(part_num)
                for sub in subs:
                    subs_result_box.insert("end", show_part(sub))
                    subs_result_box.config(width=0,height=0)
                    self.winfo_toplevel().wm_geometry("")
        
        subs_search_label = tk.Label(self, text = "Enter Part Number")
        subs_search_label.grid(column = 0, row = 0)
        
        subs_search_box = tk.Entry(self, text = "")
        subs_search_box.grid(column = 1, row = 0)
        
        subs_search_button = tk.Button(self, text = "Search", command=find_subs)
        subs_search_button.grid(column = 2, row = 0)
        
        subs_result_box = tk.Listbox(self)
        subs_result_box.grid(column = 0, row = 1, columnspan = 3, sticky = "NSEW")
            
            
if __name__ == "__main__":
    app = Main()
    app.title("partsDB")     
    app.mainloop()        
