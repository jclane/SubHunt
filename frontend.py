"""Displays the GUI for SubHunt."""
import tkinter as tk
from csv import reader as csvreader
from tkinter import ttk, messagebox, filedialog
from tkinter.ttk import Treeview, Scrollbar
from os.path import basename
from openpyxl import load_workbook
from threading import Thread
from collections import OrderedDict

from auto_hunt import copy_file, purge_subbed, get_type, save_to_file, get_all_parts
from backend import (
    remove_table,
    return_table,
    return_column_names,
    return_possible_values,
    part_in_db,
    add_part,
    remove_part,
    convert_to_dict,
    update_part,
    list_subs,
    is_valid_sub,
    import_from_csv,
    filter_columns,
    csv_writer,
)


def clear_widgets(frame):
    """Removes all widgets from frame."""
    for widget in frame.winfo_children():
        widget.destroy()


class Main(tk.Tk):
    """Displays initial state of GUI."""

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.menu = tk.Menu(self)

        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label="Import", command=self.import_list)
        self.file_menu.add_command(
            label="Purge Records", command=lambda: self.show_frame("PurgePage")
        )
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.edit = tk.Menu(self.menu, tearoff=False)
        self.edit.add_command(
            label="Add", command=lambda: self.show_frame("AddPartPage")
        )
        self.edit.add_command(
            label="Remove", command=lambda: self.show_frame("RemovePartPage")
        )
        self.edit.add_command(
            label="Edit", command=lambda: self.show_frame("EditPartPage")
        )
        self.menu.add_cascade(label="Edit", menu=self.edit)

        self.search_menu = tk.Menu(self.menu, tearoff=False)
        self.search_menu.add_command(
            label="Part Info", command=lambda: self.show_frame("SearchPage")
        )
        self.search_menu.add_command(
            label="Verify Sub", command=lambda: self.show_frame("VerifySubsPage")
        )
        self.search_menu.add_command(
            label="List Subs", command=lambda: self.show_frame("FindSubsPage")
        )
        self.search_menu.add_command(
            label="Browse", command=lambda: self.show_frame("BrowsePage")
        )
        self.search_menu.add_separator()
        self.search_menu.add_command(label="Auto Hunt", command=self.automate_sub_hunt)
        self.menu.add_cascade(label="Search", menu=self.search_menu)

        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label="Help [coming soon]")
        self.help_menu.add_command(label="About partDB [coming soon]")
        self.menu.add_cascade(label="?", menu=self.help_menu)

        self.config(menu=self.menu)

        self.container = tk.Frame(self)
        self.container.grid(column=0, row=0, sticky="EW")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for frame_name in (
            MainPage,
            PurgePage,
            AddPartPage,
            RemovePartPage,
            EditPartPage,
            SearchPage,
            VerifySubsPage,
            FindSubsPage,
            BrowsePage,
        ):
            page_name = frame_name.__name__
            frame = frame_name(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()

    def import_list(self):
        """Opens a dialog window to pick file for import"""
        file = filedialog.askopenfilename(
            title="Import", filetypes=[("CSV files", "*.csv")]
        )

        if file != "":
            import_from_csv(file)

    def automate_sub_hunt(self):
        """
        Open a dialog window to pick file for auto sub hunting then
        completes the auto-hunt.
        """

        def validate(row, all_parts):
            repair_locs = ["1320", "622", "630", "68", "67",
                            "69", "610", "615", "618", "624"]
            brands = ("ACE", "ALI", "ASU", "DEL", "GWY", "HEW", "LNV",
                      "MSS", "RCM", "RZR", "SAC", "SYC", "TSC",)

            if row[0] not in repair_locs:
                return False
            if get_type(row[31], all_parts) is None:
                return False
            if row[21] not in brands:
                return False
            if row[14] is None:
                return False
            if row[15] != row[14]:
                return False
                
            return True

        def filter_data(data, all_parts):         
            filtered = [
                [row[31], get_type(row[31], all_parts), row[14], row[13]]
                for row in data if validate(row, all_parts)
            ]
            
            return filtered

        def get_data():
            """
            Opens a menu to select the openPO report text file.  
            The file is then copied and the contents returned as a 
            list of rows.
            """
            file = filedialog.askopenfilename(
                title="Location of openPO",
                initialdir=r"%USER%\Desktop",
                filetypes=[("Plain Text", "*.txt"), ("CSV", "*.csv"),],
            )            
            
            if file:
                copied = copy_file(file)
            
            data = []
            with open(file, "r") as csvfile:
                reader = csvreader(csvfile, delimiter="\t")
                for row in reader:
                    data.append(row)
            
            return data
 
        def show_done():
            """
            Popup window informing the user that autohunt has finished.
            """
            popup = tk.Tk()
            popup.wm_title("!")
            label = ttk.Label(popup, text="DONE!", font=("Helvetica", 10))
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
            B1.pack()
            popup.mainloop()
 
        def hunter_task(popup, data):
            """
            Pulls the desired orders from the open orders report and
            displays an indeterminate progress bar to let the user know
            that the application is not frozen.  Once done the progress
            bar window is destroyed, purge_subbed is called and the
            data is saved to and Excel file.

            :param popup: Window to display the prograss bar in
            """
            tk.Label(popup, text="Working...\n").grid(row=0, column=0)
            progress_bar = ttk.Progressbar(popup, mode="indeterminate")
            progress_bar.grid(row=1, column=0)
            progress_bar.start(50)
            popup.pack_slaves()
            all_parts = get_all_parts()           
            filtered = filter_data(data[1:], all_parts)           

            save_to_file(purge_subbed(filtered))
            popup.destroy()
            show_done()

        data = get_data()
        popup = tk.Toplevel()
        t = Thread(target=hunter_task, args=(popup,data))
        t.start()


class MainPage(tk.Frame):
    """Initial page.  Is blank."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class PurgePage(tk.Frame):
    """Displays GUI for user to remove tables from database."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.db_label = tk.Label(self, text="Database to purge: ")
        self.db_label.grid(column=0, row=0, sticky="EW")

        self.db_var = tk.StringVar()
        self.db_var.set("CPU")
        self.databases = ("CPU", "HDD", "MEM")

        self.db_drop = tk.OptionMenu(self, self.db_var, *self.databases)
        self.db_drop.grid(column=1, row=0, sticky="EW")

        self.purge_button = tk.Button(self, text="Purge", command=self.purge_table)
        self.purge_button.grid(column=1, row=1, sticky="EW")

    def purge_table(self):
        """Calls remove_table to remove table from the database."""
        if remove_table(self.db_var.get().lower()):
            messagebox.showinfo("Purge Complete", self.db_var.get() + " table purged.")
        else:
            messagebox.showerror("Error!")


class AddPartPage(tk.Frame):
    """Displays GUI for users to add parts to the database."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.top_frame = tk.Frame(self)
        self.top_frame.grid(column=0, row=0, padx=5, pady=5, sticky="EW")

        self.part_info_container = tk.Frame(self)
        self.part_info_container.grid(column=0, row=1)

        self.middle_frame = tk.Frame(self.part_info_container)
        self.middle_frame.grid(column=0, row=1)

        self.entries = []
        self.string_vars = []
        self.type_specific_frame = tk.Frame(self.part_info_container)
        self.type_specific_frame.grid(column=0)

        self.bottom_frame = tk.Frame(self.part_info_container)
        self.bottom_frame.grid(column=0, row=3)

        self.part_type_label = tk.Label(self.top_frame, text="Select part type: ")
        self.part_type_label.grid(column=0, row=0, sticky="W")
        self.part_types = ["HDD", "SSD", "SSHD", "MEM", "CPU"]
        self.part_types_var = tk.StringVar()
        self.part_types_var.set("HDD")
        self.part_type_drop = tk.OptionMenu(
            self.top_frame, self.part_types_var, *self.part_types
        )
        self.part_type_drop.grid(column=1, row=0, sticky="EW")

        self.part_num_label = tk.Label(self.middle_frame, text="Part Number: ")
        self.part_num_label.grid(column=0, row=1)
        self.part_num_box = tk.Entry(self.middle_frame)
        self.part_num_box.grid(column=1, row=1, sticky="EW")

        self.brand_label = tk.Label(self.middle_frame, text="Brand: ")
        self.brand_label.grid(column=0, row=2)
        self.brand_var = tk.StringVar()
        self.string_vars.append(self.brand_var)

        self.brand_var.set("Acer")
        self.brands = (
            "Acer",
            "Asus",
            "CVO",
            "Dell",
            "Hewlett Packard",
            "Lenovo",
            "MSI",
            "Razer",
            "Samsung",
            "Sony",
            "Toshiba",
        )
        self.brand_drop = tk.OptionMenu(self.middle_frame, self.brand_var, *self.brands)
        self.brand_drop.grid(column=1, row=2, sticky="EW")

        self.description_label = tk.Label(self.middle_frame, text="Description: ")
        self.description_label.grid(column=0, row=3)
        self.description_box = tk.Entry(self.middle_frame)
        self.entries.append(self.description_box)
        self.description_box.grid(column=1, row=3)

        self.do_not_sub_var = tk.BooleanVar()
        self.do_not_sub_var.set(False)
        self.do_not_sub_check = tk.Checkbutton(
            self.bottom_frame,
            text="Do Not Sub? ",
            variable=self.do_not_sub_var,
            offvalue=False,
            onvalue=True,
            anchor="w",
        )
        self.do_not_sub_check.grid(column=1, row=0, sticky="EW")

        self.subbed_var = tk.BooleanVar()
        self.subbed_var.set(False)
        self.subbed_check = tk.Checkbutton(
            self.bottom_frame,
            text="Subbed? ",
            variable=self.subbed_var,
            offvalue=False,
            onvalue=True,
            anchor="w",
        )
        self.subbed_check.grid(column=1, row=1, sticky="EW")

        self.add_button = tk.Button(self.bottom_frame, text="Add", command=self.add_it)
        self.add_button.grid(column=1, row=2, sticky="EW")

        self.part_types_var.trace("w", self.change_dropdown)

    def storage(self):
        """
        Displays GUI for the user to add a record to the "hdd"
        table.
        """
        self.connector_label = tk.Label(self.type_specific_frame, text="Connector: ")
        self.connector_label.grid(column=0, row=0)
        self.connector_var = tk.StringVar()
        self.connector_var.set("SATA")
        self.string_vars.append(self.connector_var)
        if self.part_types_var.get() in ["HDD", "SSHD"]:
            self.connectors = ("SATA", "IDE", "proprietary")
        elif self.part_types_var.get() == "SSD":
            self.connectors = ("SATA", "m.2", "eMMC", "mSATA", "proprietary")
        self.connector_drop = tk.OptionMenu(
            self.type_specific_frame, self.connector_var, *self.connectors
        )
        self.connector_drop.grid(column=1, row=0, sticky="EW")

        self.hdd_capacity_box = tk.Entry(self.type_specific_frame)
        self.ssd_capacity_box = tk.Entry(self.type_specific_frame)
        if self.part_types_var.get() in ["HDD", "SSHD"]:
            self.entries.append(self.hdd_capacity_box)
            self.hdd_capacity_label = tk.Label(
                self.type_specific_frame, text="HDD Capacity (GB): "
            )
            self.hdd_capacity_label.grid(column=0, row=1)
            self.hdd_capacity_box.grid(column=1, row=1)
        else:
            self.hdd_capacity_box.insert(0, "")

        if self.part_types_var.get() in ["SSHD", "SSD"]:
            self.entries.append(self.ssd_capacity_box)
            self.ssd_capacity_label = tk.Label(
                self.type_specific_frame, text="SSD Capacity (GB): "
            )
            self.ssd_capacity_label.grid(column=0, row=2)
            self.ssd_capacity_box.grid(column=1, row=2)
        else:
            self.ssd_capacity_box.insert(0, "")

        self.speed_box = tk.Entry(self.type_specific_frame)
        if self.part_types_var.get() in ["HDD", "SSHD"]:
            self.entries.append(self.speed_box)
            self.speed_label = tk.Label(self.type_specific_frame, text="Speed: ")
            self.speed_label.grid(column=0, row=3)
            self.speed_box.grid(column=1, row=3)
        else:
            self.speed_box.insert(0, "")

        self.physical_size_label = tk.Label(
            self.type_specific_frame, text="Physical Size: "
        )
        self.physical_size_label.grid(column=0, row=4)
        self.physical_size_var = tk.StringVar()
        self.string_vars.append(self.physical_size_var)
        self.physical_size_var.set("2.5")
        if self.part_types_var.get() == "SSD":
            self.physical_sizes = ("2.5", "2280", "2260", "2242", "2230")
        elif self.part_types_var.get() in ["HDD", "SSHD"]:
            self.physical_sizes = ("2.5", "3.5")
        self.physical_size_drop = tk.OptionMenu(
            self.type_specific_frame, self.physical_size_var, *self.physical_sizes
        )
        self.physical_size_drop.grid(column=1, row=4, sticky="EW")

        self.height_var = tk.StringVar()
        self.string_vars.append(self.height_var)
        self.height_var.set("")

        self.height_label = tk.Label(self.type_specific_frame, text="Height: ")
        self.height_label.grid(column=0, row=5)
        self.heights = ("", "5", "7", "9.5")
        self.height_drop = tk.OptionMenu(
            self.type_specific_frame, self.height_var, *self.heights
        )
        self.height_drop.grid(column=1, row=5, sticky="EW")

        self.interface_label = tk.Label(self.type_specific_frame, text="Interface: ")
        self.interface_label.grid(column=0, row=6)
        self.interface_var = tk.StringVar()
        self.string_vars.append(self.interface_var)
        self.interface_var.set("SATA III")
        if self.part_types_var.get() == "SSD":
            self.interface_var.set("SATA")
            self.interfaces = ("SATA", "PCIe")
        elif self.part_types_var.get() in ["HDD", "SSHD"]:
            self.interfaces = ("SATA III", "SATA II", "SATA I", "SATA", "PATA")
        self.interfaces_drop = tk.OptionMenu(
            self.type_specific_frame, self.interface_var, *self.interfaces
        )
        self.interfaces_drop.grid(column=1, row=6, sticky="EW")

    def memory(self):
        """
        Displays GUI for the user to add a record to the "mem"
        table.
        """
        self.speed_label = tk.Label(self.type_specific_frame, text="Speed: ")
        self.speed_label.grid(column=0, row=0)
        self.speed_box = tk.Entry(self.type_specific_frame)
        self.entries.append(self.speed_box)
        self.speed_box.grid(column=1, row=0)

        self.connector_label = tk.Label(self.type_specific_frame, text="Connector: ")
        self.connector_label.grid(column=0, row=1)
        self.connector_var = tk.StringVar()
        self.string_vars.append(self.connector_var)
        self.connector_var.set("SO-DIMM")
        self.connectors = ("SO-DIMM", "UDIMM")
        self.connector_drop = tk.OptionMenu(
            self.type_specific_frame, self.connector_var, *self.connectors
        )
        self.connector_drop.grid(column=1, row=1, sticky="EW")

        self.capacity_label = tk.Label(self.type_specific_frame, text="Capacity (GB): ")
        self.capacity_label.grid(column=0, row=2)
        self.capacity_box = tk.Entry(self.type_specific_frame)
        self.string_vars.append(self.capacity_box)
        self.capacity_box.grid(column=1, row=2)

    def cpu(self):
        """
        Displays GUI for the user to add a record to the "cpu" table.
        """
        self.oem_label = tk.Label(self.type_specific_frame, text="OEM Part Number: ")
        self.oem_label.grid(column=0, row=0)

        self.oem_box = tk.Entry(self.type_specific_frame)
        self.entries.append(self.oem_box)
        self.oem_box.grid(column=1, row=0)

    def set_label_width(self):
        """
        Sets the width of each label in the container frame to match
        the longest label.
        """
        width = 0
        for frame in self.part_info_container.winfo_children():
            for widget in frame.winfo_children():
                if widget.winfo_class() == "Label":
                    if width < len(widget.cget("text")):
                        width = len(widget.cget("text"))
        for frame in self.part_info_container.winfo_children():
            for widget in frame.winfo_children():
                if widget.winfo_class() == "Label":
                    widget.configure(width=width - 2)
                    widget.configure(anchor="e")

    def clear_fields(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        for str_var in self.string_vars:
            str_var.set("")

    def add_it(self):
        if self.part_types_var.get() in ["HDD", "SSD", "SSHD"]:
            self.part_info = (
                self.part_num_box.get().strip(),
                self.brand_var.get(),
                self.connector_var.get(),
                self.hdd_capacity_box.get(),
                self.ssd_capacity_box.get(),
                self.speed_box.get(),
                self.part_types_var.get(),
                self.physical_size_var.get(),
                self.height_var.get(),
                self.interface_var.get(),
                self.description_box.get(),
                str(bool(self.do_not_sub_var.get())).upper(),
                str(bool(self.subbed_var.get())).upper(),
            )
            self.table = "hdd"
        elif self.part_types_var.get() == "MEM":
            self.part_info = (
                self.part_num_box.get(),
                self.speed_box.get(),
                self.brand_var.get(),
                self.connector_var.get(),
                self.capacity_box.get(),
                self.description_box.get(),
                str(bool(self.do_not_sub_var.get())).upper(),
                str(bool(self.subbed_var.get())).upper(),
            )
            self.table = "mem"
        elif self.part_types_var.get() == "CPU":
            self.part_info = (
                self.part_num_box.get(),
                self.brand_var.get(),
                self.description_box.get(),
                self.oem_box.get(),
                str(bool(self.do_not_sub_var.get())).upper(),
                str(bool(self.subbed_var.get())).upper(),
            )
            self.table = "cpu"
        if add_part(self.table, self.part_info) == "Done":
            self.clear_fields()
            messagebox.showinfo(
                "Part Added",
                self.part_num_box.get().strip() + " has been added to the database.",
            )

    def change_dropdown(self, *args):
        """
        When a part type/table is selected from the dropdown
        all widgets are removed from sub_frame and appropriate
        method is called.
        """
        clear_widgets(self.type_specific_frame)
        if self.part_types_var.get() in ["HDD", "SSD", "SSHD"]:
            self.storage()
        elif self.part_types_var.get() == "MEM":
            self.memory()
        elif self.part_types_var.get() == "CPU":
            self.cpu()
        self.set_label_width()


class RemovePartPage(tk.Frame):
    """
    Displays the GUI allowing users to remove parts from the
    database.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Remove Part"

        self.part_num_label = tk.Label(self, text="Enter Part Number: ")
        self.part_num_label.grid(column=0, row=0)

        self.part_num_box = tk.Entry(self)
        self.part_num_box.grid(column=1, row=0)

        self.part_type_var = tk.StringVar()
        self.part_type_var.set("HDD")
        self.part_types = ["HDD", "MEM", "CPU"]

        self.part_type_drop = tk.OptionMenu(self, self.part_type_var, *self.part_types)
        self.part_type_drop.grid(column=3, row=0)

        self.remove_button = tk.Button(self, text="Remove", command=self.remove_it)
        self.remove_button.grid(column=4, row=0)

    def remove_it(self):
        """
        Retreives table and part_num field data and uses it
        to call remove_part.
        """
        self.part_num = self.part_num_box.get().strip()
        self.table = self.part_type_var.get()
        if (
            self.part_num != ""
            and part_in_db(self.table, self.part_num)
            and remove_part(self.table, self.part_num) == "Done"
        ):
            messagebox.showinfo("Part Removed", self.part_num + " removed successfuly.")
        elif self.part_num == "":
            messagebox.showerror("Invalid Entry", "Please enter a part number.")
        elif not part_in_db(self.table, self.part_num):
            messagebox.showerror(
                "Invalid Entry", self.part_num + " does not exist in the database."
            )


class EditPartPage(tk.Frame):
    """
    Displays GUI allowing the user to edit details of a record
    already in the database.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.container = tk.Frame(self)
        self.container.grid(column=0, row=0, sticky="EW")
        self.sub_frame = tk.Frame(self)
        self.sub_frame.grid(column=0, row=1, sticky="EW")
        self.updated_part_dict = OrderedDict()

        self.info_search_label = tk.Label(self.container, text="Enter Part Number: ")
        self.info_search_label.grid(column=0, row=0, sticky="EW")
        self.info_search_box = tk.Entry(self.container, text="")
        self.info_search_box.grid(column=1, row=0, sticky="EW")

        self.info_type_var = tk.StringVar()
        self.info_type_var.set("HDD")
        self.info_types = ("HDD", "MEM", "CPU")
        self.info_type_drop = tk.OptionMenu(
            self.container, self.info_type_var, *self.info_types
        )
        self.info_type_drop.grid(column=2, row=0, sticky="EW")

        self.info_search_button = tk.Button(
            self.container,
            text="Search",
            command=lambda: self.show_part_info(self.info_search_box.get().strip()),
        )
        self.info_search_button.grid(column=3, row=0, sticky="EW")

        self.save_button = tk.Button(
            self.container,
            text="Save",
            command=lambda: self.save_it(self.updated_part_dict),
        )
        self.save_button.grid(column=4, row=0, sticky="EW")

    def save_it(self, updated_info):
        """
        Creates of tuple of the dictionary passed to then uses that
        data to call update_part.

        :param updated_info: Dictionary with desired changes
        """
        
        self.part_info = tuple(value.get() for key, value in updated_info.items())
        if update_part(self.info_type_var.get().lower(), self.part_info) == "Done":
            messagebox.showinfo(
                "Part Update", self.info_search_box.get().strip() + " has been updated."
            )

    def show_part_info(self, part_num):
        """
        Displays the part info in the GUI in a visually appealing
        way.  Will display an error message if the part passed to
        it is not in the database.

        :param part_num: Part number to be edited
        """
        clear_widgets(self.sub_frame)
        self.table = self.info_type_var.get().lower()
        if part_num != "" and part_in_db(self.table, part_num):
            self.part_info = convert_to_dict(self.table, part_num)
            for row_num, key in enumerate(self.part_info):
                if key in ["do_not_sub", "subbed"]:
                    self.part_info[key] = str(self.part_info[key]).upper()

                if key == "part_num":
                    _ = tk.Entry(self.sub_frame)
                    _.grid(column=1, row=row_num, sticky="W")
                    _.insert(0, self.part_info[key])
                    _.config(state="disabled")
                    self.updated_part_dict["part_num"] = _
                elif key == "brand":
                    self.brand_var = tk.StringVar()
                    self.brand_var.set(self.part_info[key])
                    self.brands = (
                        "Acer",
                        "Asus",
                        "CVO",
                        "Dell",
                        "Hewlett Packard",
                        "Lenovo",
                        "MSI",
                        "Razer",
                        "Samsung",
                        "Sony",
                        "Toshiba",
                    )
                    tk.OptionMenu(self.sub_frame, self.brand_var, *self.brands).grid(
                        column=1, row=row_num, sticky="W"
                    )
                    self.updated_part_dict["brand"] = self.brand_var
                elif key == "connector":
                    if self.table == "hdd":
                        connectors = (
                            "SATA",
                            "m.2",
                            "eMMC",
                            "mSATA",
                            "IDE",
                            "proprietary",
                        )
                    elif self.table == "mem":
                        connectors = ("SO-DIMM", "UDIMM")
                    connector_var = tk.StringVar()
                    connector_var.set(self.part_info[key])

                    tk.OptionMenu(self.sub_frame, connector_var, *connectors).grid(
                        column=1, row=row_num, sticky="W"
                    )
                    self.updated_part_dict["connector"] = connector_var
                elif key == "type":
                    self.type_var = tk.StringVar()
                    self.type_var.set(self.part_info[key])
                    self.types = ("HDD", "SSD", "SSHD")
                    tk.OptionMenu(self.sub_frame, self.type_var, *self.types).grid(
                        column=1, row=row_num, sticky="W"
                    )
                    self.updated_part_dict["type"] = self.type_var
                else:
                    _ = tk.Entry(self.sub_frame)
                    _.grid(column=1, row=row_num, sticky="W")
                    _.insert(0, self.part_info[key])
                    self.updated_part_dict[key] = _

                tk.Label(self.sub_frame, text=key).grid(
                    column=0, row=row_num, sticky="W"
                )
        elif part_num == "":
            messagebox.showerror("Invalid Entry", "Please enter a part number.")
        elif not part_in_db(self.table, part_num):
            messagebox.showerror(
                "Invalid Entry", part_num + " does not exist in the database."
            )


class SearchPage(tk.Frame):
    """
    Displays a GUI allowing users to search the database for a given
    record and display data for that record.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Find Part Info"

        self.container = tk.Frame(self)
        self.container.grid(column=0, row=0, sticky="EW")

        self.sub_frame = tk.Frame(self)
        self.sub_frame.grid(column=0, row=1, sticky="EW")

        self.info_search_label = tk.Label(self.container, text="Enter Part Number: ")
        self.info_search_label.grid(column=0, row=0, sticky="EW")

        self.info_search_box = tk.Entry(self.container, text="")
        self.info_search_box.grid(column=1, row=0, sticky="EW")

        self.info_type_var = tk.StringVar()
        self.info_type_var.set("HDD")
        self.info_types = ("HDD", "MEM", "CPU")

        self.info_type_drop = tk.OptionMenu(
            self.container, self.info_type_var, *self.info_types
        )
        self.info_type_drop.grid(column=2, row=0, sticky="EW")

        self.info_search_button = tk.Button(
            self.container,
            text="Search",
            command=lambda: self.show_part_info(self.info_search_box.get().strip()),
        )
        self.info_search_button.grid(column=3, row=0, sticky="EW")

    def show_part_info(self, part_num):
        """
        Displays data for part_num on the frame.  Will return an
        error message if part is not in the database.

        :param part_num: Part number to search for
        """
        clear_widgets(self.sub_frame)
        self.table = self.info_type_var.get().lower()
        if part_num != "" and part_in_db(self.table, part_num):
            self.part_dict = convert_to_dict(self.table, part_num)
            self.part_info = {
                key: value for key, value in self.part_dict.items() if value != ""
            }
            for row_num, key in enumerate(self.part_info):
                if key in ["do_not_sub", "subbed"]:
                    self.part_info[key] = str(self.part_info[key]).upper()
                tk.Label(self.sub_frame, text=key).grid(
                    column=0, row=row_num, sticky="W"
                )
                tk.Label(self.sub_frame, text=self.part_info[key]).grid(
                    column=1, row=row_num, sticky="W"
                )
        elif part_num == "":
            messagebox.showerror("Invalid Entry", "Please enter a part number.")
        elif not part_in_db(self.table, part_num):
            messagebox.showerror(
                "Invalid Entry", part_num + " does not exist in the database."
            )


class VerifySubsPage(tk.Frame):
    """Displays if two entered part numbers are valid subs."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Verify Subs"

        self.search_frame = tk.Frame(self)
        self.search_frame.grid(column=0, row=0, sticky="EW")

        self.part_num_label = tk.Label(self.search_frame, text="Enter Part Number")
        self.part_num_label.grid(column=0, row=0)

        self.part_num_box = tk.Entry(self.search_frame, text="")
        self.part_num_box.grid(column=1, row=0)

        self.other_part_label = tk.Label(self.search_frame, text="Enter Second Part")
        self.other_part_label.grid(column=0, row=1)

        self.other_part_box = tk.Entry(self.search_frame, text="")
        self.other_part_box.grid(column=1, row=1)

        self.subs_type_var = tk.StringVar()
        self.subs_type_var.set("HDD")
        self.subs_types = ("HDD", "MEM", "CPU")

        self.subs_type_drop = tk.OptionMenu(
            self.search_frame, self.subs_type_var, *self.subs_types
        )
        self.subs_type_drop.grid(column=0, row=2)

        self.subs_search_button = tk.Button(
            self.search_frame,
            text="Verify",
            command=lambda: self.verify_sub(
                self.subs_type_var.get().lower(),
                self.part_num_box.get().strip(),
                self.other_part_box.get().strip(),
            ),
        )
        self.subs_search_button.grid(column=1, row=2)

    def show_result(self, result):
        """
        Displays True or False depending on result.

        :param result: Boolean
        """
        if result:
            bg_color = "green"
        if not result:
            bg_color = "red"
        self.result_label = tk.Label(
            self.search_frame, text=str(result), bg=bg_color, font=24
        )
        self.result_label.grid(column=0, row=3, columnspan=2, sticky="NSEW")

    def verify_sub(self, table, part_num, other_part_num):
        """
        Calls is_valid_sub using table, part_num, and
        other_part_num and calls show_result with the result.

        :param table: Table in database
        :param part_num: Part number
        :param other_part_num: Part number to compare
        """
        if part_num and other_part_num:
            self.show_result(is_valid_sub(table, part_num, other_part_num))
        else:
            messagebox.showerror(
                "All fields required",
                "Please enter data in both part number \
                                 fields.",
            )


class FindSubsPage(tk.Frame):
    """
    Displays the matching subs for a given part number in the GUI.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Find Subs"

        self.search_frame = tk.Frame(self)
        self.search_frame.grid(column=0, row=0, sticky="EW")

        self.results = tk.Frame(self)
        self.results.grid(column=0, row=1, padx=20, pady=10, sticky="EW")

        self.subs_search_label = tk.Label(self.search_frame, text="Enter Part Number")
        self.subs_search_label.grid(column=0, row=0)

        self.subs_search_box = tk.Entry(self.search_frame, text="")
        self.subs_search_box.grid(column=1, row=0)

        self.subs_type_var = tk.StringVar()
        self.subs_type_var.set("HDD")
        self.subs_types = ("HDD", "MEM", "CPU")

        self.subs_type_drop = tk.OptionMenu(
            self.search_frame, self.subs_type_var, *self.subs_types
        )
        self.subs_type_drop.grid(column=2, row=0)

        self.subs_search_button = tk.Button(
            self.search_frame,
            text="Search",
            command=lambda: self.find_subs(self.subs_search_box.get().strip()),
        )
        self.subs_search_button.grid(column=3, row=0)

    def make_table(self, table, subs):
        """
        Displays list of a subs in a spreadsheet
        like manner.

        :param table: Name of database table
        :param part_num: Part number
        :param subs: List of parts matching specs
            of part_num
        """
        clear_widgets(self.results)

        if table == "hdd":
            headers = [
                "Brand",
                "Part Number",
                "Type",
                "Deminsions",
                "Height",
                "Connector",
                "HDD (GB)",
                "SSD (GB)",
                "Speed",
                "Subbed?",
            ]
        elif table == "mem":
            headers = [
                "Brand",
                "Part Number",
                "Connector",
                "Capacity",
                "Speed",
                "Subbed?",
            ]
        elif table == "cpu":
            headers = ["Brand", "Part Number", "OEM", "Description", "Subbed?"]

        self.widths = {}
        for col_num in enumerate(subs[0]):
            columns = []
            for sub in subs:
                columns.append(sub[col_num[0]])
                self.widths[col_num[0]] = max(len(element) for element in columns)
            self.label_width = max(self.widths[col_num[0]], len(headers[col_num[0]]))
            if self.widths[col_num[0]] < self.label_width:
                self.widths[col_num[0]] = self.label_width + 2

        for col, header in enumerate(headers):
            tk.Label(
                self.results, text=header, width=self.widths[col], justify="center"
            ).grid(column=col, row=0)

        for row, sub in enumerate(subs):
            if row % 2 == 0:
                bg_color = "snow3"
            else:
                bg_color = "snow2"

            if sub[-1] == "TRUE":
                fg_color = "green4"
            else:
                fg_color = "Red2"

            if sub[0] == "CVO":
                fg_color = "steelblue"

            for col, info in enumerate(sub):
                info_var = tk.StringVar()
                info_var.set(info)
                tk.Entry(
                    self.results,
                    width=self.widths[col] + 2,
                    textvariable=info_var,
                    readonlybackground=bg_color,
                    foreground=fg_color,
                    relief="flat",
                    justify="center",
                    state="readonly",
                ).grid(column=col, row=row + 1, sticky="EW")

    def find_subs(self, part_num):
        """
        Finds subs for part_num in the database.
        Then calls make_table to display them.

        :param part_num: Part number to find subs for
        """
        self.table = self.subs_type_var.get().lower()
        if part_num != "" and part_in_db(self.table, part_num):
            subs = list_subs(self.table, part_num)
            if subs:
                self.make_table(self.table, subs)
        elif not part_in_db(self.table, part_num):
            messagebox.showerror(
                "Invalid Entry", part_num + " does not exist in the database."
            )


class BrowsePage(tk.Frame):
    """
    Displays treeview with all parts listed for a given table.
    """

    def __init__(self, parent, controller):
        self.specs = []
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.type_frame = tk.Frame(self)
        self.type_frame.grid(column=0, row=0, sticky="EW")

        self.filter_frame = tk.Frame(self)
        self.filter_frame.grid(column=0, row=1, sticky="EW")

        self.results_frame = tk.Frame(self)
        self.results_frame.grid(column=0, row=2, padx=20, pady=10, sticky="NSEW")
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)

        self.result_count = tk.StringVar()
        self.table_var = tk.StringVar()
        self.tables = ("HDD", "MEM", "CPU")

        self.table_type_drop = tk.OptionMenu(
            self.type_frame, self.table_var, *self.tables
        )
        self.table_type_drop.grid(column=0, row=0)

        self.table_var.trace("w", self.handle_table_change)
        self.table_var.set("HDD")

    def fill_table(self, parts):
        """
        Displays list of a parts from a table in a spreadsheet
        like manner.

        :param parts: List of parts
            of part_num
        """
        clear_widgets(self.filter_frame)
        self.results_tv.delete(*self.results_tv.get_children())

        self.headers = return_column_names(self.table_var.get())
        self.results_tv["columns"] = self.headers

        for header in enumerate(self.headers):
            self.results_tv.column("#" + str(header[0]), width=len(header[1]) * 10)
            self.results_tv.heading("#" + str(header[0]), text=header[1])

        self.results_tv.column("#" + str(len(self.headers)), minwidth=0, width=0, stretch=False)

        for part in parts:
            self.results_tv.insert("", tk.END, text=part[0], values=part[1:])

    def OnDoubleClick(self, event):
        item = self.results_tv.selection()[0]
        self.clipboard_append(self.results_tv.item(item,"text"))

    def build_treeview(self):
        clear_widgets(self.results_frame)
        self.results_tv = Treeview(self.results_frame, columns=1, height=20)
        self.results_tv.pack(expand=True, fill="both")
        self.result_label = tk.Label(self.results_frame, textvariable=self.result_count)
        self.result_label.pack(side="bottom")
        vsb = Scrollbar(
            self.results_tv, orient="vertical", command=self.results_tv.yview
        )
        vsb.place(x=1, y=25, height=400)
        self.results_tv.bind("<Double-1>", self.OnDoubleClick)

    def make_buttons(self, table):
        """
        Make buttons for filtering data

        :param table:  Table in sqlite3 db
        """
        self.var_dict = {}
        columns = return_column_names(table)
        for column_name in enumerate(columns):
            self.var_dict[column_name[1]] = tk.StringVar()
            self.var_dict[column_name[1]].set(column_name[1])
            _ = tk.OptionMenu(
                self.filter_frame,
                self.var_dict[column_name[1]],
                *return_possible_values(table, column_name[1])
            )
            _.configure(width=len(column_name[1]))
            _.grid(column=column_name[0], row=0, sticky="EW")
            self.var_dict[column_name[1]].trace("w", self.handle_filter_change)
        tk.Button(self.type_frame, text="Export", command=self.save_to_file).grid(
            column=2, row=0
        )

    def save_to_file(self):
        rows = [self.headers]
        for child in self.results_tv.get_children():
            _templst = self.results_tv.item(child)["values"]
            _templst.insert(0, self.results_tv.item(child)["text"])
            rows.append(_templst)
        csv_writer("exported_list.csv", rows)

    def handle_filter_change(self, *args):
        multi_filter = {}
        for k, v in self.var_dict.items():
            if k != v.get():
                multi_filter[k] = v.get()
        parts = filter_columns(self.table_var.get(), multi_filter)
        self.results_tv.delete(*self.results_tv.get_children())
        for part in parts:
            self.results_tv.insert("", tk.END, text=part[0], values=part[1:])

        self.result_count.set(str(len(parts)))

        tk.Button(
            self.type_frame, text="Clear Filters", command=self.handle_reset
        ).grid(column=1, row=0)

    def handle_table_change(self, *args):
        parts = return_table(self.table_var.get())
        self.result_count.set(str(len(parts)))
        self.build_treeview()
        self.fill_table(parts)
        self.make_buttons(self.table_var.get())

    def handle_reset(self):
        clear_widgets(self.filter_frame)
        self.handle_table_change()