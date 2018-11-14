"""Displays the GUI for SubHunt."""

import tkinter as tk
from tkinter import messagebox, filedialog

from backend import (remove_table, part_in_db, add_part, remove_part,
                     convert_to_dict, update_part, list_subs,
                     is_valid_sub, import_from_csv)


def clear_widgets(frame):
    """Removes all widgets from frame."""
    for widget in frame.winfo_children():
        widget.destroy()


class Main(tk.Tk):
    """Displays initial state of GUI."""

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Import", command=self.import_list)
        file_menu.add_command(label="Purge Records",
                              command=lambda: self.show_frame("PurgePage"))
        menu.add_cascade(label="File", menu=file_menu)

        edit = tk.Menu(menu, tearoff=False)
        edit.add_command(label="Add",
                         command=lambda: self.show_frame("AddPartPage"))
        edit.add_command(label="Remove",
                         command=lambda: self.show_frame("RemovePartPage"))
        edit.add_command(label="Edit",
                         command=lambda: self.show_frame("EditPartPage"))
        menu.add_cascade(label="Edit", menu=edit)

        search_menu = tk.Menu(menu, tearoff=False)
        search_menu.add_command(
            label="Part Info", command=lambda: self.show_frame("SearchPage"))
        search_menu.add_command(
            label="Verify Sub", command=lambda: self.show_frame("VerifySubsPage"))
        search_menu.add_command(
            label="List Subs", command=lambda: self.show_frame("FindSubsPage")
            )
        menu.add_cascade(label="Search", menu=search_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Help [coming soon]")
        help_menu.add_command(label="About partDB [coming soon]")
        menu.add_cascade(label="?", menu=help_menu)

        self.config(menu=menu)
        self.geometry("860x525")

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="EW")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for frame_name in (MainPage, PurgePage, AddPartPage, RemovePartPage,
                           EditPartPage, SearchPage, VerifySubsPage,
                           FindSubsPage):
            page_name = frame_name.__name__
            frame = frame_name(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()

    def import_list(self):
        """Opens a dialog window to pick file for import"""
        file = filedialog.askopenfilename(title="Import",
                                          filetypes=[("CSV files", "*.csv")])

        if file != "":
            import_from_csv(file)


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

        def purge_table():
            """Calls remove_table to remove table from the database."""

            if remove_table(db_var.get().lower()):
                messagebox.showinfo("Purge Complete",
                                    db_var.get() + " table purged.")
            else:
                messagebox.showerror("Error!")

        db_label = tk.Label(self, text="Database to purge: ")
        db_label.grid(column=0, row=0, sticky="EW")

        db_var = tk.StringVar()
        db_var.set("CPU")
        databases = ("CPU", "HDD", "MEM")

        db_drop = tk.OptionMenu(self, db_var, *databases)
        db_drop.grid(column=1, row=0, sticky="EW")

        purge_button = tk.Button(
            self,
            text="Purge",
            command=purge_table
            )
        purge_button.grid(column=1, row=1, sticky="EW")


class AddPartPage(tk.Frame):
    """Displays GUI for users to add parts to the database."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="EW")

        sub_frame = tk.Frame(self)
        sub_frame.grid(column=0, row=1, padx=5, pady=5)

        part_type_label = tk.Label(container, text="Select part type: ")
        part_type_label.grid(column=0, row=0, sticky="W")
        part_types = ["HDD", "SSD", "SSHD", "MEM", "CPU"]
        part_types_var = tk.StringVar()
        part_types_var.set("HDD")
        part_type_drop = tk.OptionMenu(container, part_types_var, *part_types)
        part_type_drop.grid(column=1, row=0, sticky="EW")

        def add_hdd():
            """
            Displays GUI for the user to add a record to the "hdd"
            table.
            """

            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)
            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="EW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)
            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")
            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="EW")

            description_label = tk.Label(sub_frame, text="Description: ")
            description_label.grid(column=0, row=3)
            description_box = tk.Entry(sub_frame)
            description_box.grid(column=1, row=3)

            connector_label = tk.Label(sub_frame, text="Connector: ")
            connector_label.grid(column=0, row=4)
            connector_var = tk.StringVar()
            connector_var.set("SATA")
            if part_types_var.get() in ["HDD", "SSHD"]:
                connectors = ("SATA", "IDE", "proprietary")
            elif part_types_var.get() == "SSD":
                connectors = ("SATA", "m.2", "eMMC", "mSATA", "proprietary")
            connector_drop = tk.OptionMenu(sub_frame, connector_var,
                                           *connectors)
            connector_drop.grid(column=1, row=4)

            hdd_capacity_box = tk.Entry(sub_frame)
            ssd_capacity_box = tk.Entry(sub_frame)
            if part_types_var.get() in ["HDD", "SSHD"]:
                hdd_capacity_label = tk.Label(
                    sub_frame, text="HDD Capacity (GB): "
                    )
                hdd_capacity_label.grid(column=0, row=5)
                hdd_capacity_box.grid(column=1, row=5)
            else:
                hdd_capacity_box.insert(0, "")

            if part_types_var.get() in ["SSHD", "SSD"]:
                ssd_capacity_label = tk.Label(sub_frame,
                                              text="SSD Capacity (GB): ")
                ssd_capacity_label.grid(column=0, row=6)
                ssd_capacity_box.grid(column=1, row=6)
            else:
                ssd_capacity_box.insert(0, "")

            speed_box = tk.Entry(sub_frame)
            if part_types_var.get() in ["HDD", "SSHD"]:
                speed_label = tk.Label(sub_frame, text="Speed: ")
                speed_label.grid(column=0, row=7)
                speed_box.grid(column=1, row=7)
            else:
                speed_box.insert(0, "")

            physical_size_label = tk.Label(sub_frame, text="Physical Size: ")
            physical_size_label.grid(column=0, row=8)
            physical_size_var = tk.StringVar()
            physical_size_var.set("2.5")
            if part_types_var.get() == "SSD":
                physical_sizes = ("2.5", "2280", "2260", "2242", "2230")
            elif part_types_var.get() in ["HDD", "SSHD"]:
                physical_sizes = ("2.5", "3.5")
            physical_size_drop = tk.OptionMenu(sub_frame, physical_size_var,
                                               *physical_sizes)
            physical_size_drop.grid(column=1, row=8)

            height_var = tk.StringVar()
            height_var.set("")

            height_label = tk.Label(sub_frame, text="Height: ")
            height_label.grid(column=0, row=9)
            heights = ("5", "7", "9.5")
            height_drop = tk.OptionMenu(sub_frame, height_var, *heights)
            height_drop.grid(column=1, row=9)

            interface_label = tk.Label(sub_frame, text="Interface: ")
            interface_label.grid(column=0, row=10)
            interface_var = tk.StringVar()
            interface_var.set("SATA III")
            if part_types_var.get() == "SSD":
                interface_var.set("SATA")
                interfaces = ("SATA", "PCIe")
            elif part_types_var.get() in ["HDD", "SSHD"]:
                interfaces = ("SATA III", "SATA II", "SATA I", "SATA", "PATA")
            interfaces_drop = tk.OptionMenu(sub_frame, interface_var,
                                            *interfaces)
            interfaces_drop.grid(column=1, row=10)

            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)
            do_not_sub_check = tk.Checkbutton(sub_frame, text="Do Not Sub? ",
                                              variable=do_not_sub_var,
                                              anchor="w")
            do_not_sub_check.grid(column=1, row=11, sticky="EW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)
            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, anchor="w")
            subbed_check.grid(column=1, row=12, sticky="EW")

            def add_it():
                part_info = (part_num_box.get().strip(), brand_var.get(),
                             connector_var.get(), hdd_capacity_box.get(),
                             ssd_capacity_box.get(), speed_box.get(),
                             part_types_var.get(), physical_size_var.get(),
                             height_var.get(), interface_var.get(),
                             description_box.get(),
                             str(bool(do_not_sub_var.get())).upper(),
                             str(bool(subbed_var.get())).upper())
                if add_part("hdd", part_info) == "Done":
                    messagebox.showinfo("Part Added",
                                        part_num_box.get().strip() +
                                        " has been added to the database.")

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=13, sticky="EW")

        def add_mem():
            """
            Displays GUI for the user to add a record to the "mem"
            table.
            """

            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)

            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="EW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)

            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")

            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="EW")

            description_label = tk.Label(sub_frame, text="Description: ")
            description_label.grid(column=0, row=3)

            description_box = tk.Entry(sub_frame)
            description_box.grid(column=1, row=3)

            speed_label = tk.Label(sub_frame, text="Speed: ")
            speed_label.grid(column=0, row=4)

            speed_box = tk.Entry(sub_frame)
            speed_box.grid(column=1, row=4)

            connector_label = tk.Label(sub_frame, text="Connector: ")
            connector_label.grid(column=0, row=5)

            connector_var = tk.StringVar()
            connector_var.set("SO-DIMM")
            connectors = ("SO-DIMM", "UDIMM")

            connector_drop = tk.OptionMenu(sub_frame, connector_var,
                                           *connectors)
            connector_drop.grid(column=1, row=5)

            capacity_label = tk.Label(sub_frame, text="Capacity (GB): ")
            capacity_label.grid(column=0, row=6)

            capacity_box = tk.Entry(sub_frame)
            capacity_box.grid(column=1, row=6)

            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)

            do_not_sub_check = tk.Checkbutton(sub_frame, text="Do Not Sub? ",
                                              variable=do_not_sub_var,
                                              offvalue=False, onvalue=True,
                                              anchor="w")
            do_not_sub_check.grid(column=1, row=7, sticky="EW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)

            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, offvalue=False,
                                          onvalue=True, anchor="w")
            subbed_check.grid(column=1, row=8, sticky="EW")

            def add_it():
                part_info = (part_num_box.get(), speed_box.get(),
                             brand_var.get(), connector_var.get(),
                             capacity_box.get(), description_box.get(),
                             str(bool(do_not_sub_var.get())).upper(),
                             str(bool(subbed_var.get())).upper())
                add_part("mem", part_info)

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=9, sticky="EW")

        def add_cpu():
            """
            Displays GUI for the user to add a record to the "cpu"
                table.
            """

            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)

            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="EW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)

            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")

            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="EW")

            description_label = tk.Label(sub_frame, text="Description: ")
            description_label.grid(column=0, row=3)

            description_box = tk.Entry(sub_frame)
            description_box.grid(column=1, row=3)

            oem_label = tk.Label(sub_frame, text="OEM Part Number: ")
            oem_label.grid(column=0, row=3)

            oem_box = tk.Entry(sub_frame)
            oem_box.grid(column=1, row=3)

            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)

            do_not_sub_check = tk.Checkbutton(sub_frame, text="Do Not Sub? ",
                                              variable=do_not_sub_var,
                                              offvalue=False, onvalue=True,
                                              anchor="w")
            do_not_sub_check.grid(column=1, row=7, sticky="EW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)

            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, offvalue=False,
                                          onvalue=True, anchor="w")
            subbed_check.grid(column=1, row=8, sticky="EW")

            def add_it():
                part_info = (part_num_box.get(), brand_var.get(),
                             description_box.get(), oem_box.get(),
                             str(bool(do_not_sub_var.get())).upper(),
                             str(bool(subbed_var.get())).upper())
                add_part("cpu", part_info)

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=9, sticky="EW")

        def change_dropdown():
            """
            When a part type/table is selected from the dropdown
                all widgets are removed from sub_frame and appropriate
                method is called.
            """
            clear_widgets(sub_frame)
            if part_types_var.get() in ["HDD", "SSD", "SSHD"]:
                clear_widgets(sub_frame)
                add_hdd()
            elif part_types_var.get() == "MEM":
                clear_widgets(sub_frame)
                add_mem()
            elif part_types_var.get() == "CPU":
                clear_widgets(sub_frame)
                add_cpu()

        part_types_var.trace('w', change_dropdown)


class RemovePartPage(tk.Frame):
    """
    Displays the GUI allowing users to remove parts from the
    database.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Remove Part"

        def remove_it():
            """
            Retreives table and part_num field data and uses it
            to call remove_part.
            """
            part_num = part_num_box.get().strip()
            table = part_type_var.get()
            if (part_num != "" and part_in_db(table, part_num) and
                    remove_part(table, part_num) == "Done"):
                messagebox.showinfo("Part Removed", part_num +
                                    " removed successfuly.")
            elif part_num == "":
                messagebox.showerror("Invalid Entry",
                                     "Please enter a part number.")
            elif not part_in_db(table, part_num):
                messagebox.showerror("Invalid Entry",
                                     part_num +
                                     " does not exist in the database.")

        part_num_label = tk.Label(self, text="Enter Part Number: ")
        part_num_label.grid(column=0, row=0)

        part_num_box = tk.Entry(self)
        part_num_box.grid(column=1, row=0)

        part_type_var = tk.StringVar()
        part_type_var.set("HDD")
        part_types = ["HDD", "MEM", "CPU"]

        part_type_drop = tk.OptionMenu(self, part_type_var, *part_types)
        part_type_drop.grid(column=3, row=0)

        remove_button = tk.Button(self, text="Remove", command=remove_it)
        remove_button.grid(column=4, row=0)


class EditPartPage(tk.Frame):
    """
    Displays GUI allowing the user to edit details of a record
    already in the database.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="EW")
        sub_frame = tk.Frame(self)
        sub_frame.grid(column=0, row=1, sticky="EW")
        updated_part_dict = {}

        def save_it(updated_info):
            """
            Creates of tuple of the dictionary passed to then uses that
            data to call update_part.

            :param updated_info: Dictionary with desired changes
            """
            part_info = tuple(value.get() for key, value
                              in updated_info.items())
            if update_part(info_type_var.get().lower(), part_info) == "Done":
                messagebox.showinfo("Part Update",
                                    info_search_box.get().strip() +
                                    " has been updated.")

        def show_part_info(part_num):
            """
            Displays the part info in the GUI in a visually appealing
            way.  Will display an error message if the part passed to
            it is not in the database.
            """
            clear_widgets(sub_frame)
            table = info_type_var.get().lower()
            if part_num != "" and part_in_db(table, part_num):
                part_info = convert_to_dict(table, part_num)
                for row_num, key in enumerate(part_info):
                    if key in ["do_not_sub", "subbed"]:
                        part_info[key] = str(part_info[key]).upper()

                    if key == "part_num":
                        _ = tk.Entry(sub_frame)
                        _.grid(column=1, row=row_num, sticky="W")
                        _.insert(0, part_info[key])
                        _.config(state="disabled")
                        updated_part_dict["part_num"] = _
                    elif key == "brand":
                        brand_var = tk.StringVar()
                        brand_var.set(part_info[key])
                        brands = ("Acer", "Asus", "CVO", "Dell",
                                  "Hewlett Packard", "Lenovo", "Samsung",
                                  "Sony", "Toshiba")
                        tk.OptionMenu(sub_frame, brand_var, *brands).grid(
                            column=1, row=row_num, sticky="W")
                        updated_part_dict["brand"] = brand_var
                    elif key == "connector":
                        connector_var = tk.StringVar()
                        connector_var.set(part_info[key])
                        connectors = ("SATA", "m.2", "eMMC", "mSATA",
                                      "IDE", "proprietary")
                        tk.OptionMenu(sub_frame, connector_var,
                                      *connectors).grid(column=1, row=row_num,
                                                        sticky="W")
                        updated_part_dict["connector"] = connector_var
                    elif key == "type":
                        type_var = tk.StringVar()
                        type_var.set(part_info[key])
                        types = ("HDD", "SSD", "SSHD")
                        tk.OptionMenu(sub_frame, type_var,
                                      *types).grid(column=1, row=row_num,
                                                   sticky="W")
                        updated_part_dict["type"] = type_var
                    else:
                        _ = tk.Entry(sub_frame)
                        _.grid(column=1, row=row_num, sticky="W")
                        _.insert(0, part_info[key])
                        updated_part_dict[key] = _

                    tk.Label(sub_frame, text=key).grid(column=0, row=row_num,
                                                       sticky="W")
            elif part_num == "":
                messagebox.showerror("Invalid Entry",
                                     "Please enter a part number.")
            elif not part_in_db(table, part_num):
                messagebox.showerror("Invalid Entry",
                                     part_num +
                                     " does not exist in the database.")

        info_search_label = tk.Label(container, text="Enter Part Number: ")
        info_search_label.grid(column=0, row=0, sticky="EW")
        info_search_box = tk.Entry(container, text="")
        info_search_box.grid(column=1, row=0, sticky="EW")

        info_type_var = tk.StringVar()
        info_type_var.set("HDD")
        info_types = ("HDD", "MEM", "CPU")
        info_type_drop = tk.OptionMenu(container, info_type_var, *info_types)
        info_type_drop.grid(column=2, row=0, sticky="EW")

        info_search_button = tk.Button(container, text="Search",
                                       command=lambda:
                                       show_part_info(info_search_box.get()
                                                      .strip()))
        info_search_button.grid(column=3, row=0, sticky="EW")

        save_button = tk.Button(container, text="Save",
                                command=lambda: save_it(updated_part_dict))
        save_button.grid(column=4, row=0, sticky="EW")


class SearchPage(tk.Frame):
    """
    Displays a GUI allowing users to search the database for a given
    record and display data for that record.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Find Part Info"

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="EW")

        sub_frame = tk.Frame(self)
        sub_frame.grid(column=0, row=1, sticky="EW")

        def show_part_info(part_num):
            """
            Displays data for part_num on the frame.  Will return an
            error message if part is not in the database.

            :param part_num: Part number to search for
            """
            clear_widgets(sub_frame)
            table = info_type_var.get().lower()
            if part_num != "" and part_in_db(table, part_num):
                part_dict = convert_to_dict(table, part_num)
                part_info = {
                    key: value for key, value in part_dict.items()
                    if value != ""
                    }
                for row_num, key in enumerate(part_info):
                    if key in ["do_not_sub", "subbed"]:
                        part_info[key] = str(part_info[key]).upper()
                    tk.Label(sub_frame, text=key).grid(column=0, row=row_num,
                                                       sticky="W")
                    tk.Label(sub_frame, text=part_info[key]).grid(column=1,
                                                                  row=row_num,
                                                                  sticky="W")
            elif part_num == "":
                messagebox.showerror("Invalid Entry",
                                     "Please enter a part number.")
            elif not part_in_db(table, part_num):
                messagebox.showerror("Invalid Entry",
                                     part_num +
                                     " does not exist in the database.")

        info_search_label = tk.Label(container, text="Enter Part Number: ")
        info_search_label.grid(column=0, row=0, sticky="EW")

        info_search_box = tk.Entry(container, text="")
        info_search_box.grid(column=1, row=0, sticky="EW")

        info_type_var = tk.StringVar()
        info_type_var.set("HDD")
        info_types = ("HDD", "MEM", "CPU")

        info_type_drop = tk.OptionMenu(container, info_type_var, *info_types)
        info_type_drop.grid(column=2, row=0, sticky="EW")

        info_search_button = tk.Button(container, text="Search",
                                       command=lambda:
                                       show_part_info(info_search_box.get()
                                                      .strip()))
        info_search_button.grid(column=3, row=0, sticky="EW")


class VerifySubsPage(tk.Frame):
    """Displays if two entered part numbers are valid subs."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Verify Subs"

        search_frame = tk.Frame(self)
        search_frame.grid(column=0, row=0, sticky="EW")

        def show_result(result):
            """
            Displays True or False depending on result.

            :param result: Boolean
            """
            if result:
                bg_color = "green"
            if not result:
                bg_color = "red"
            result_label = tk.Label(search_frame, text=str(result),
                                    bg=bg_color, font=24)
            result_label.grid(column=0, row=3, columnspan=2, sticky="NSEW")

        def verify_sub(table, part_num, other_part_num):
            """
            Calls is_valid_sub using table, part_num, and
            other_part_num and calls show_result with the result.

            :param table: Table in database
            :param part_num: Part number
            :param other_part_num: Part number to compare
            """
            if part_num and other_part_num:
                show_result(is_valid_sub(table, part_num, other_part_num))
            else:
                messagebox.showerror("All fields required", "Please enter data in both part number fields.")

        part_num_label = tk.Label(search_frame, text="Enter Part Number")
        part_num_label.grid(column=0, row=0)

        part_num_box = tk.Entry(search_frame, text="")
        part_num_box.grid(column=1, row=0)

        other_part_label = tk.Label(search_frame, text="Enter Second Part")
        other_part_label.grid(column=0, row=1)

        other_part_box = tk.Entry(search_frame, text="")
        other_part_box.grid(column=1, row=1)

        subs_type_var = tk.StringVar()
        subs_type_var.set("HDD")
        subs_types = ("HDD", "MEM", "CPU")

        subs_type_drop = tk.OptionMenu(search_frame, subs_type_var,
                                       *subs_types)
        subs_type_drop.grid(column=0, row=2)

        subs_search_button = tk.Button(search_frame, text="Verify",
                                       command=lambda:
                                       verify_sub(subs_type_var.get().lower(),
                                                  part_num_box.get().strip(),
                                                  other_part_box.get()
                                                  .strip()))
        subs_search_button.grid(column=1, row=2)


class FindSubsPage(tk.Frame):
    """
    Displays the matching subs for a given part number in the GUI.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "SubHunt | Find Subs"

        search_frame = tk.Frame(self)
        search_frame.grid(column=0, row=0, sticky="EW")

        results = tk.Frame(self)
        results.grid(column=0, row=1, padx=20, pady=10, sticky="EW")

        def make_table(table, subs):
            """
            Displays list of a subs in a spreadsheet
            like manner.

            :param table: Name of database table
            :param part_num: Part number
            :param subs: List of parts matching specs
                of part_num
            """
            clear_widgets(results)
            if table == "hdd":
                headers = ["Brand", "Part Number", "Type", "Deminsions",
                           "Height", "Connector", "HDD (GB)", "SSD (GB)",
                           "Speed", "Subbed?"]
            elif table == "mem":
                headers = ["Brand", "Part Number", "Connector", "Capacity",
                           "Speed", "Subbed?"]
            elif table == "cpu":
                headers = ["Brand", "Part Number", "OEM", "Description",
                           "Subbed?"]

            widths = {}
            for col_num in enumerate(subs[0]):
                columns = []
                for sub in subs:
                    columns.append(sub[col_num[0]])
                    widths[col_num[0]] = max(len(element) for element in columns)
                label_width = max(widths[col_num[0]], len(headers[col_num[0]]))
                if widths[col_num[0]] < label_width:
                    widths[col_num[0]] = label_width + 2

            for col, header in enumerate(headers):
                tk.Label(results, text=header,
                         width=widths[col],
                         justify="center").grid(column=col, row=0)

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
                    tk.Entry(results, width=widths[col] + 2,
                             textvariable=info_var,
                             readonlybackground=bg_color,
                             foreground=fg_color,
                             relief="flat", justify="center",
                             state="readonly").grid(column=col, row=row + 1,
                                                    sticky="EW")

        def find_subs(part_num):
            """
            Finds subs for part_num in the database.
            Then calls make_table to display them.
            """
            table = subs_type_var.get().lower()
            if part_num != "" and part_in_db(table, part_num):
                subs = list_subs(table, part_num)
                if subs:
                    make_table(table, subs)
            elif not part_in_db(table, part_num):
                messagebox.showerror("Invalid Entry",
                                     part_num +
                                     " does not exist in the database.")

        subs_search_label = tk.Label(search_frame, text="Enter Part Number")
        subs_search_label.grid(column=0, row=0)

        subs_search_box = tk.Entry(search_frame, text="")
        subs_search_box.grid(column=1, row=0)

        subs_type_var = tk.StringVar()
        subs_type_var.set("HDD")
        subs_types = ("HDD", "MEM", "CPU")

        subs_type_drop = tk.OptionMenu(search_frame, subs_type_var,
                                       *subs_types)
        subs_type_drop.grid(column=2, row=0)

        subs_search_button = tk.Button(search_frame, text="Search",
                                       command=lambda:
                                       find_subs(subs_search_box.get()
                                                 .strip()))
        subs_search_button.grid(column=3, row=0)
