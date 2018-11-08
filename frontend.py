from backend import *

import tkinter as tk


def import_list():
    """Opens a dialog window to pick file for import"""

    file = tk.filedialog.askopenfilename(title="Import",
                                         filetypes=[("CSV files", "*.csv")])

    if file != "":
        import_from_csv(file)


def clear_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Import", command=import_list)
        file_menu.add_command(label="Purge Records",
                              command=lambda: self.show_frame("PurgePage"))
        menu.add_cascade(label="File", menu=file_menu)

        edit = tk.Menu(menu, tearoff=False)
        edit.add_command(label="Add",
                         command=lambda: self.show_frame("AddPartPage"))
        edit.add_command(label="Remove")
        edit.add_command(label="Edit")
        menu.add_cascade(label="Edit", menu=edit)

        search_menu = tk.Menu(menu, tearoff=False)
        search_menu.add_command(
            label="Part Info", command=lambda: self.show_frame("SearchPage"))
        search_menu.add_command(label="Verify Sub")
        search_menu.add_command(
            label="List Subs", command=lambda: self.show_frame("FindSubsPage")
            )
        menu.add_cascade(label="Search", menu=search_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Help")
        help_menu.add_command(label="About partDB")
        menu.add_cascade(label="?", menu=help_menu)

        self.config(menu=menu)
        self.geometry("750x500")

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="NSEW")
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
        self.grid(padx=5, pady=5)

        db_label = tk.Label(self, text="Database to purge: ")
        db_label.grid(column=0, row=0, sticky="NSEW")

        db_var = tk.StringVar()
        db_var.set("CPU")
        databases = ("CPU", "HDD", "MEM")

        db_drop = tk.OptionMenu(self, db_var, *databases)
        db_drop.grid(column=1, row=0, sticky="NSEW")

        purge_button = tk.Button(
            self,
            text="Purge",
            command=lambda: remove_table(db_var.get().lower())
            )
        purge_button.grid(column=1, row=1, sticky="NSEW")


class AddPartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="NSEW")

        sub_frame = tk.Frame(self)
        sub_frame.grid(column=0, row=1, padx=5, pady=5)

        part_type_label = tk.Label(container, text="Select part type: ")
        part_type_label.grid(column=0, row=0, sticky="W")

        part_types = ["HDD", "SSD", "SSHD", "MEM", "CPU"]
        part_types_var = tk.StringVar()
        part_types_var.set("HDD")

        part_type_drop = tk.OptionMenu(container, part_types_var, *part_types)
        part_type_drop.grid(column=1, row=0, sticky="NSEW")

        def add_hdd():

            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)

            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="NSEW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)

            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")

            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="NSEW")

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

            speed_label = tk.Label(sub_frame, text="Speed: ")
            speed_label.grid(column=0, row=7)

            speed_box = tk.Entry(sub_frame)
            speed_box.grid(column=1, row=7)

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

            height_label = tk.Label(sub_frame, text="Height: ")
            height_label.grid(column=0, row=9)

            height_var = tk.StringVar()
            height_var.set("")
            heights = (5, 7, 9)

            height_drop = tk.OptionMenu(sub_frame, height_var, *heights)
            height_drop.grid(column=1, row=9)

            interface_label = tk.Label(sub_frame, text="Interface: ")
            interface_label.grid(column=0, row=10)

            interface_var = tk.StringVar()
            interface_var.set("SATA III")

            if part_types_var.get() == "SSD":
                interfaces = ("SATA", "PCIE")
            elif part_types_var.get() in ["HDD", "SSHD"]:
                interfaces = ("SATA III", "SATA II", "SATA I", "SATA", "PATA")

            interfaces_drop = tk.OptionMenu(sub_frame, interface_var,
                                            *interfaces)
            interfaces_drop.grid(column=1, row=10)

            do_not_sub_var = tk.BooleanVar()
            do_not_sub_var.set(False)

            do_not_sub_check = tk.Checkbutton(sub_frame, text="Do Not Sub? ",
                                              variable=do_not_sub_var,
                                              offvalue=False, onvalue=True,
                                              anchor="w")
            do_not_sub_check.grid(column=1, row=11, sticky="NSEW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)

            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, offvalue=False,
                                          onvalue=True, anchor="w")
            subbed_check.grid(column=1, row=12, sticky="NSEW")

            def add_it():
                part_info = (part_num_box.get(), brand_var.get(),
                             connector_var.get(), hdd_capacity_box.get(),
                             ssd_capacity_box.get(), speed_box.get(),
                             part_types_var.get(), physical_size_var.get(),
                             height_var.get(), interface_var.get(),
                             description_box.get(), do_not_sub_var.get(),
                             subbed_var.get())
                add_part("hdd", part_info)

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=13, sticky="NSEW")

        def add_mem():
            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)

            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="NSEW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)

            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")

            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="NSEW")

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
            do_not_sub_check.grid(column=1, row=7, sticky="NSEW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)

            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, offvalue=False,
                                          onvalue=True, anchor="w")
            subbed_check.grid(column=1, row=8, sticky="NSEW")

            def add_it():
                part_info = (part_num_box.get(), speed_box.get(),
                             brand_var.get(), connector_var.get(),
                             capacity_box.get(), description_box.get(),
                             do_not_sub_var.get(), subbed_var.get())
                add_part("mem", part_info)

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=9, sticky="NSEW")

        def add_cpu():
            part_num_label = tk.Label(sub_frame, text="Part Number: ")
            part_num_label.grid(column=0, row=1)

            part_num_box = tk.Entry(sub_frame)
            part_num_box.grid(column=1, row=1, sticky="NSEW")

            brand_label = tk.Label(sub_frame, text="Brand: ")
            brand_label.grid(column=0, row=2)

            brand_var = tk.StringVar()
            brand_var.set("Acer")
            brands = ("Acer", "Asus", "CVO", "Dell", "Hewlett Packard",
                      "Lenovo", "Samsung", "Sony", "Toshiba")

            brand_drop = tk.OptionMenu(sub_frame, brand_var, *brands)
            brand_drop.grid(column=1, row=2, sticky="NSEW")

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
            do_not_sub_check.grid(column=1, row=7, sticky="NSEW")

            subbed_var = tk.BooleanVar()
            subbed_var.set(False)

            subbed_check = tk.Checkbutton(sub_frame, text="Subbed? ",
                                          variable=subbed_var, offvalue=False,
                                          onvalue=True, anchor="w")
            subbed_check.grid(column=1, row=8, sticky="NSEW")

            def add_it():
                part_info = (part_num_box.get(), brand_var.get(),
                             description_box.get(), oem_box.get(),
                             do_not_sub_var.get(), subbed_var.get())
                add_part("cpu", part_info)

            add_button = tk.Button(sub_frame, text="Add", command=add_it)
            add_button.grid(column=1, row=9, sticky="NSEW")

        def change_dropdown(*args):
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


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Part Info"

        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky="NSEW")

        sub_frame = tk.Frame(self)
        sub_frame.grid(column=0, row=1, sticky="NSEW")

        def show_part_info():
            clear_widgets(sub_frame)
            part_num = info_search_box.get()
            table = info_type_var.get().lower()
            if part_num != "":
                part_dict = convert_to_dict(table, part_num)
                part_info = {
                    key: value for key, value in part_dict.items()
                    if value != ""
                    }
                for row_num, key in enumerate(part_info):
                    if key in ["do_not_sub", "subbed"]:
                        part_info[key] = str(bool(part_info[key]))
                    tk.Label(sub_frame, text=key).grid(column=0, row=row_num,
                                                       sticky="W")
                    tk.Label(sub_frame, text=part_info[key]).grid(column=1,
                                                                  row=row_num,
                                                                  sticky="W")

        info_search_label = tk.Label(container, text="Enter Part Number: ")
        info_search_label.grid(column=0, row=0, sticky="NSEW")

        info_search_box = tk.Entry(container, text="")
        info_search_box.grid(column=1, row=0, sticky="NSEW")

        info_type_var = tk.StringVar()
        info_type_var.set("HDD")
        info_types = ("HDD", "MEM", "CPU")

        info_type_drop = tk.OptionMenu(container, info_type_var, *info_types)
        info_type_drop.grid(column=2, row=0, sticky="NSEW")

        info_search_button = tk.Button(container, text="Search",
                                       command=show_part_info)
        info_search_button.grid(column=3, row=0, sticky="NSEW")


class FindSubsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "partsDB | Find Subs"

        search_frame = tk.Frame(self)
        search_frame.grid(column=0, row=0, sticky="NSEW")

        results = tk.Frame(self)
        results.grid(column=0, row=1, padx=20, pady=10, sticky="NSEW")

        def make_table(table, part_num, subs):
            """
            Displays list of a subs in a spreadsheet
            like manner.

            :param table: Name of database table
            :param part_num: Part number
            :param subs: List of parts matching specs
                of part_num
            """
            clear_widgets(results)

            part_info = convert_to_dict(table, part_num)

            if table == "hdd":
                if part_info["type"] == "HDD":
                    headers = ["Brand", "Part Number", "Type", "Deminsions",
                               "Height", "Connector", "Capacity (GB)",
                               "Speed", "Subbed?"]
                elif part_info["type"] == "SSD":
                    headers = ["Brand", "Part Number", "Type", "Deminsions",
                               "Connector", "Capacity (GB)", "Subbed?"]
                elif part_info["type"] == "SSHD":
                    headers = ["Brand", "Part Number", "Type", "Height",
                               "Connector", "HDD Capacity (GB)",
                               "SSD Capacity", "Speed", "Subbed?"]
            elif table == "mem":
                headers = ["Brand", "Part Number", "Connector", "Capacity",
                           "Speed", "Subbed?"]
            elif table == "cpu":
                headers = ["Brand", "Part Number", "OEM", "Description",
                           "Subbed?"]

            widths = {}
            for col_num in range(0, len(subs[0])):
                columns = []
                for sub in subs:
                    columns.append(sub[col_num])
                widths[col_num] = max(len(element) for element in columns)
                label_width = max(widths[col_num], len(headers[col_num]))
                if widths[col_num] < label_width:
                    widths[col_num] = label_width + 2
                tk.Label(results, text=headers[col_num],
                         width=widths[col_num],
                         justify="center").grid(column=col_num, row=0)

            for row, sub in enumerate(subs):
                for col, info in enumerate(sub):
                    info_var = tk.StringVar()
                    info_var.set(info)
                    tk.Entry(results, width=widths[col] + 2,
                             textvariable=info_var, relief="flat",
                             justify="center",
                             state="readonly").grid(column=col, row=row + 1)

        def find_subs():
            part_num = subs_search_box.get()
            table = subs_type_var.get().lower()
            if part_num != "":
                subs = list_subs(table, part_num)
                make_table(table, part_num, subs)

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
                                       command=find_subs)
        subs_search_button.grid(column=3, row=0)


if __name__ == "__main__":
    app = Main()
    app.title("partsDB")
    app.mainloop()
