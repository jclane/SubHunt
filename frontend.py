from backend import *

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

        
def import_list():
    """Opens a dialog window to pick file"""

    file = tk.filedialog.askopenfilename(title="Import", filetypes=[("CSV files", "*.csv")])
    
    if file != "":
        import_from_csv(file)

  
class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
    
        tk.Tk.__init__(self, *args, **kwargs)
               
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Import", command=import_list)
        file_menu.add_command(label="Purge Records", command= lambda: self.show_frame("PurgePage"))
        menu.add_cascade(label="File", menu=file_menu)

        edit = tk.Menu(menu, tearoff=False)
        edit.add_command(label="Add", command=lambda: self.show_frame("AddPartPage"))
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
        
        for F in (MainPage, PurgePage, AddPartPage, SearchPage, FindSubsPage):
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


class PurgePage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller    
        self.grid(padx = 5, pady = 5)
        
        db_label = tk.Label(self, text = "Database to purge: ")
        db_label.grid(column = 0, row = 0, sticky = "NSEW")
        
        db_var = tk.StringVar()
        db_var.set("CPU")
        databases = ("CPU", "HDD", "MEM")
        
        db_drop = tk.OptionMenu(self, db_var, *databases)
        db_drop.grid(column = 1, row = 0, sticky = "NSEW")
        
        purge_button = tk.Button(self, text = "Purge", command = lambda: purge(db_var.get().lower()))
        purge_button.grid(column = 1, row = 1, sticky = "NSEW")        
        

class AddPartPage(tk.Frame):  # Lots of changes needed here.
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
                        
        part_type_label = tk.Label(self, text="Select part type: ")
        part_type_label.grid(column = 0, row = 0, sticky = "W")
        
        part_types  = ["HDD", "SSD", "SSHD", "MEM", "CPU"]
        part_types_var = tk.StringVar()
        part_types_var.set("HDD")
        
        part_type_drop = tk.OptionMenu(self, part_types_var, *part_types)
        part_type_drop.grid(column = 1, row = 0, sticky = "NSEW")                

        sub_frame = tk.Frame(self)
        sub_frame.grid(column = 0, row = 1, padx = 5, pady = 5)
        
        def add_hdd():
            
            part_num_label = tk.Label(sub_frame, text = "Part Number: ")
            part_num_label.grid(column = 0, row = 1)
            
            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column = 1, row = 1, sticky = "NSEW")
                       
            brand_label = tk.Label(sub_frame, text = "Brand: ")
            brand_label.grid(column = 0, row = 2)
            
            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard", 
                    "Lenovo", "Samsung", "Sony", "Toshiba")
            
            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column = 1, row = 2, sticky = "NSEW")
            
            description_label = tk.Label(sub_frame, text = "Description: ")
            description_label.grid(column = 0, row = 3)
            
            description_box = tk.Entry(sub_frame)
            description_box.grid(column = 1, row = 3)
            
            connector_label = tk.Label(sub_frame, text = "Connector: ")
            connector_label.grid(column = 0, row = 4)
            
            connector_var = tk.StringVar()
            connector_var.set("SATA")
            connectors = ("SATA", "IDE", "proprietary")
            
            connector_drop = tk.OptionMenu(sub_frame, connector_var, *connectors)
            connector_drop.grid(column = 1, row = 4)
            
            hdd_capacity_label = tk.Label(sub_frame, text = "HDD Capacity (GB): ")
            hdd_capacity_label.grid(column = 0, row = 5)
            
            hdd_capacity_box = tk.Entry(sub_frame)
            hdd_capacity_box.grid(column = 1, row = 5)
            
            if part_types_var.get() == "SSHD":
                ssd_capacity_label = tk.Label(sub_frame, text = "SSD Capacity (GB): ")
                ssd_capacity_label.grid(column = 0, row = 6)
                
                ssd_capacity_box = tk.Entry(sub_frame)
                ssd_capacity_box.grid(column = 1, row = 6)
            
            speed_label = tk.Label(sub_frame, text = "Speed: ")
            speed_label.grid(column = 0, row = 7)
            
            speed_box = tk.Entry(sub_frame)
            speed_box.grid(column = 1, row = 7) 
            
            physical_size_label = tk.Label(sub_frame, text = "Physical Size: ")
            physical_size_label.grid(column = 0, row = 8)
            
            physical_size_var = tk.StringVar()
            physical_size_var.set("2.5")
            physical_sizes = ("2.5", "3.5")
            
            physical_size_drop = tk.OptionMenu(sub_frame, physical_size_var, *physical_sizes)
            physical_size_drop.grid(column = 1, row = 8)
            
            height_label = tk.Label(sub_frame, text = "Height: ")
            height_label.grid(column = 0, row = 9)
            
            height_var = tk.StringVar()
            height_var.set("")
            heights = (5, 7, 9)

            height_drop = tk.OptionMenu(sub_frame, height_var, *heights)
            height_drop.grid(column = 1, row = 9)
            
            interface_label = tk.Label(sub_frame, text = "Interface: ")
            interface_label.grid(column = 0, row = 10)
            
            interface_var = tk.StringVar()
            interface_var.set("SATA III")
            interfaces = ("SATA III", "SATA II", "SATA I", "SATA", "PATA")
            
            interfaces_drop = tk.OptionMenu(sub_frame, interface_var, *interfaces)
            interfaces_drop.grid(column = 1, row = 10)
            
            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)
            
            do_not_sub_check = tk.Checkbutton(sub_frame, text = "Do Not Sub? ", 
                                variable = do_not_sub_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            do_not_sub_check.grid(column = 1, row = 11, sticky = "NSEW")
                        
            subbed_var = tk.BooleanVar()
            subbed_var.set(False)
            
            subbed_check = tk.Checkbutton(sub_frame, text = "Subbed? ", 
                                variable = subbed_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            subbed_check.grid(column = 1, row = 12, sticky = "NSEW")
            
            
            def add_it():               
                if part_types_var.get() == "HDD":
                    part_info = (part_num_box.get(), brand_var.get(), description_box.get(), connector_var.get(), hdd_capacity_box.get(), speed_box.get(),
                                physical_size_var.get(), height_var.get(), interface_var.get(), do_not_sub_var.get(), subbed_var.get())
                    add_part(part_num_box.get(), Harddrive(*part_info))
                elif part_types_var.get() == "SSHD":
                    part_info = (part_num_box.get(), brand_var.get(), description_box.get(), connector_var.get(), hdd_capacity_box.get(), ssd_capacity_box.get(), speed_box.get(),
                                physical_size_var.get(), height_var.get(), interface_var.get(), do_not_sub_var.get(), subbed_var.get())
                    add_part(part_num_box.get(), HybridDrive(*part_info))        
                
                
            add_button = tk.Button(sub_frame, text = "Add", command = add_it)
            add_button.grid(column = 1, row = 13, sticky = "NSEW")
        
        
        def add_ssd():
            part_num_label = tk.Label(sub_frame, text = "Part Number: ")
            part_num_label.grid(column = 0, row = 1)
            
            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column = 1, row = 1, sticky = "NSEW")
                       
            brand_label = tk.Label(sub_frame, text = "Brand: ")
            brand_label.grid(column = 0, row = 2)
            
            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard", 
                    "Lenovo", "Samsung", "Sony", "Toshiba")
            
            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column = 1, row = 2, sticky = "NSEW")
            
            description_label = tk.Label(sub_frame, text = "Description: ")
            description_label.grid(column = 0, row = 3)
            
            description_box = tk.Entry(sub_frame)
            description_box.grid(column = 1, row = 3)
            
            connector_label = tk.Label(sub_frame, text = "Connector: ")
            connector_label.grid(column = 0, row = 4)
            
            connector_var = tk.StringVar()
            connector_var.set("SATA")
            connectors = ("SATA", "m.2", "eMMC", "mSATA", "proprietary")
            
            connector_drop = tk.OptionMenu(sub_frame, connector_var, *connectors)
            connector_drop.grid(column = 1, row = 4)
            
            ssd_capacity_label = tk.Label(sub_frame, text = "SSD Capacity (GB): ")
            ssd_capacity_label.grid(column = 0, row = 5)
                
            ssd_capacity_box = tk.Entry(sub_frame)
            ssd_capacity_box.grid(column = 1, row = 5)
            
            physical_size_label = tk.Label(sub_frame, text = "Physical Size: ")
            physical_size_label.grid(column = 0, row = 6)
            
            physical_size_var = tk.StringVar()
            physical_size_var.set("2.5")
            physical_sizes = ("2.5", "2280", "2260", "2242", "2230")
            
            physical_size_drop = tk.OptionMenu(sub_frame, physical_size_var, *physical_sizes)
            physical_size_drop.grid(column = 1, row = 6)
            
            height_label = tk.Label(sub_frame, text = "Height: ")
            height_label.grid(column = 0, row = 7)
            
            height_var = tk.StringVar()
            height_var.set("")
            heights = (5, 7, 9)

            height_drop = tk.OptionMenu(sub_frame, height_var, *heights)
            height_drop.grid(column = 1, row = 7)
            
            interface_label = tk.Label(sub_frame, text = "Interface: ")
            interface_label.grid(column = 0, row = 8)
            
            interface_var = tk.StringVar()
            interface_var.set("SATA")
            interfaces = ("SATA", "PCIE")
            
            interfaces_drop = tk.OptionMenu(sub_frame, interface_var, *interfaces)
            interfaces_drop.grid(column = 1, row = 8)
            
            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)
            
            do_not_sub_check = tk.Checkbutton(sub_frame, text = "Do Not Sub? ", 
                                variable = do_not_sub_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            do_not_sub_check.grid(column = 1, row = 9, sticky = "NSEW")
                        
            subbed_var = tk.BooleanVar()
            subbed_var.set(False)
            
            subbed_check = tk.Checkbutton(sub_frame, text = "Subbed? ", 
                                variable = subbed_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            subbed_check.grid(column = 1, row = 10, sticky = "NSEW")
            
            
            def add_it():               
                part_info = (part_num_box.get(), brand_var.get(), description_box.get(), connector_var.get(), ssd_capacity_box.get(),
                            physical_size_var.get(), height_var.get(), interface_var.get(), do_not_sub_var.get(), subbed_var.get())
                add_part("ssd_db", part_num_box.get(), SolidStateDrive(*part_info))   
                
            
            add_button = tk.Button(sub_frame, text = "Add", command = add_it)
            add_button.grid(column = 1, row = 11, sticky = "NSEW")
            

        def add_mem():           
            part_num_label = tk.Label(sub_frame, text = "Part Number: ")
            part_num_label.grid(column = 0, row = 1)
            
            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column = 1, row = 1, sticky = "NSEW")
                       
            brand_label = tk.Label(sub_frame, text = "Brand: ")
            brand_label.grid(column = 0, row = 2)
            
            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard", 
                    "Lenovo", "Samsung", "Sony", "Toshiba")
            
            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column = 1, row = 2, sticky = "NSEW")
                        
            description_label = tk.Label(sub_frame, text = "Description: ")
            description_label.grid(column = 0, row = 3)
            
            description_box = tk.Entry(sub_frame)
            description_box.grid(column = 1, row = 3)
            
            speed_label = tk.Label(sub_frame, text = "Speed: ")
            speed_label.grid(column = 0, row = 4)
            
            speed_box = tk.Entry(sub_frame)
            speed_box.grid(column = 1, row = 4)
            
            connector_label = tk.Label(sub_frame, text = "Connector: ")
            connector_label.grid(column = 0, row = 5)
            
            connector_var = tk.StringVar()
            connector_var.set("SATA")
            connectors = ("SATA", "m.2", "eMMC", "mSATA", "proprietary")
            
            connector_drop = tk.OptionMenu(sub_frame, connector_var, *connectors)
            connector_drop.grid(column = 1, row = 5)
            
            capacity_label = tk.Label(sub_frame, text = "Capacity (GB): ")
            capacity_label.grid(column = 0, row = 6)
                
            capacity_box = tk.Entry(sub_frame)
            capacity_box.grid(column = 1, row = 6)
  
            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)
            
            do_not_sub_check = tk.Checkbutton(sub_frame, text = "Do Not Sub? ", 
                                variable = do_not_sub_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            do_not_sub_check.grid(column = 1, row = 7, sticky = "NSEW")
                        
            subbed_var = tk.BooleanVar()
            subbed_var.set(False)
            
            subbed_check = tk.Checkbutton(sub_frame, text = "Subbed? ", 
                                variable = subbed_var, offvalue = False, 
                                onvalue = True, anchor = "w")
            subbed_check.grid(column = 1, row = 8, sticky = "NSEW")
            
            def add_it():               
                part_info = (part_num_box.get(), speed_box.get(), brand_var.get(), connector_var.get(), capacity_box.get(),
                            description_box.get(), do_not_sub_var.get(), subbed_var.get())
                add_part("mem_db", part_num_box.get(), Memory(*part_info))   
                
            
            add_button = tk.Button(sub_frame, text = "Add", command = add_it)
            add_button.grid(column = 1, row = 9, sticky = "NSEW")
            
        def add_cpu():
            pass
            # TODO : Add cpu page
            
        
        def clear_widets(frame):
            for widget in frame.winfo_children():
                widget.destroy()
        
        
        def change_dropdown(*args):
            clear_widets(sub_frame)
            if part_types_var.get() == "HDD" or part_types_var.get() == "SSHD":
                add_hdd()
            elif part_types_var.get() == "SSD":
                add_ssd()
            elif part_types_var.get() == "MEM":
                add_mem()
            elif part_types_var.get() == "CPU":
                add_cpu()
                
                
        part_types_var.trace('w', change_dropdown)


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Part Info"
        
        def part_info():
            part_num = info_search_box.get()
            table = info_type_var.get().lower()
            
            if part_num != "":
                part_info = convert_to_dict(table, part_num)
                num = 1
                for key in part_info:
                    tk.Label(self, text = key).grid(column = 0, row = num)
                    tk.Label(self, text = part_info[key]).grid(column = 1, row = num)
                    num += 1
                  
        
        info_search_label = tk.Label(self, text = "Enter Part Number")
        info_search_label.grid(column = 0, row = 0)
        
        info_search_box = tk.Entry(self, text="")
        info_search_box.grid(column = 1, row = 0)
        
        info_type_var = tk.StringVar()
        info_type_var.set("HDD")
        info_types = ("HDD", "MEM", "CPU")
        
        info_type_drop = tk.OptionMenu(self, info_type_var, *info_types)
        info_type_drop.grid(column = 2, row = 0)
        
        info_search_button = tk.Button(self, text="Search", command=part_info)
        info_search_button.grid(column = 3, row = 0)
        

class FindSubsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Subs"
        
        def find_subs():
            part_num = subs_search_box.get()
            table = subs_type_var.get().lower()
            
            if part_num != "":
                subs = list_subs(table, part_num)
                for sub in subs:
                    subs_result_box.insert("end", sub)
                    subs_result_box.config(width=0,height=0)
                    self.winfo_toplevel().wm_geometry("")
        
        subs_search_label = tk.Label(self, text = "Enter Part Number")
        subs_search_label.grid(column = 0, row = 0)
        
        subs_search_box = tk.Entry(self, text = "")
        subs_search_box.grid(column = 1, row = 0)
        
        subs_type_var = tk.StringVar()
        subs_type_var.set("HDD")
        subs_types = ("HDD", "MEM", "CPU")
        
        subs_type_drop = tk.OptionMenu(self, subs_type_var, *subs_types)
        subs_type_drop.grid(column = 2, row = 0)
        
        subs_search_button = tk.Button(self, text = "Search", command=find_subs)
        subs_search_button.grid(column = 3, row = 0)
        
        subs_result_box = tk.Listbox(self)
        subs_result_box.grid(column = 0, row = 1, columnspan = 3, sticky = "NSEW")
            
            
if __name__ == "__main__":
    app = Main()
    app.title("partsDB")     
    app.mainloop()        
