from datetime import date
from os.path import basename
from os.path import join as pathjoin
from pathlib import Path
from shutil import copyfile
from tkinter import filedialog


def auto_hunt(hunt_type):

    def copy_file(original):
        """
        Copies file to the appropriate location and returns the path of the copy.

        :param original: Path of the file to be copied
        :return: Path for the new local copy
        """
        report = "Parts Planning" if basename(original).startswith("Parts Planning") else "openPO"
        subdir = f"{report} Reports"
        filename = pathjoin(f"{subdir}", report + f" {str(dt.date.today())}{Path(original).suffix}")
        local_copy = copyfile(original, pathjoin(r".\reports", f"{filename}"))
        return local_copy

    def copy_and_return_file(initdir):
        """
        Opens file dialog box at 'initdir'. Once a file is selected 'copy_file'
        is called and the path to the copy is returned or 'None'.

        :param original: Path to the file to be copied
        :return: Path to the copy or 'None'
        """
        file = filedialog.askopenfilename(
            title=f"Select desired report",
            initialdir=initdir,
            filetypes=[("CSV", "*.csv"),("Excel", "*.xlsx")],
        )
        if file:
            file_copy = copy_file(file)
        else:
            return None

        return file_copy

    def read_po(path):
        """
        This reads the 'Open PO' report with the *.csv file type and returns a list of part
        objects.

        :param path: Path to the file to open
        :return: List of part objects
        """
        data = []
        try:
            with open(path, "r") as csvfile:
                reader = csv_DictReader(csvfile)
                for row in reader:
                    new_row = {}
                    for k,v in row.items():
                        new_row[k.replace("ï»¿", "").replace("txt", "").replace(" ", "").replace("#", "", 1)] = v
                    data.append(new_row)
        except IOError as e:
            print(e)

        return data

    def read_pp(path):
        """
        This reads the 'Parts Planning' excel report and returns a list of part
        objects.

        NOTE: Part class string 'PROC' must be change to 'CPU' for this to work
        with the existing database.

        :param path: Path to the file to open
        :return: List of part objects
        """
        data = []
        try:
            wb = load_workbook(filename=path, read_only=True)
            try:
                ws = wb["All_Combined"]
                for row in ws.iter_rows(min_row=6):
                    relevant = (row[0].value, row[2].value,
                                row[3].value, row[31].value,)
                    if all(relevant) and not relevant[2] == "-":
                        pclass = relevant[1]
                        if pclass == "PROC":
                            pclass = "CPU"
                        data.append({"pn":relevant[0],
                                     "class":pclass,
                                     "brand":relevant[2]})
            finally:
                wb.close()
        except IOError as e:
            print(e)
            
        return data

    def read_file(hunt_type, path):
        """
        Calls either 'read_po' or read_pp' based on 'hunt_type' and returns
        list of part objects or 'None'.

        :param hunt_type: String indicating which function to callable
        :param path: Path to the report to read
        :return: A list or part objects or 'None'
        """
        if hunt_type == "po":
            return read_po(path)
        if hunt_type == "pp":
            return read_pp(path)

        return None

    def get_data(hunt_type):
        """
        Sets 'initdir' based on 'hunt_type' and calls 'copy_and_return_file'
        to copy the desired report and return the path to the copy. Afterwards,
        the copy is read and contents returned.

        :param hunt_type: String indicating report type
        :return: List of objects representing parts
        """
        if hunt_type == "po":
            initdir = r"[REDACTED]"
        elif hunt_type == "pp":
            initdir = r"[REDACTED]"
        else:
            initdir = r"."
    
        path = copy_and_return_file(initdir)
        data = read_file(hunt_type, path)

        return data

    def validate(data):
        """
        Validates that 'data' has acceptable values for coverage, location,
        brand, and class.

        :param data: Object representing a partition
        :return: Boolean true/false
        """
        coverage = ["MFG WARRANTY", "PSP"]
        classes = ["MEM", "HDD", "SSD", "PROC", "CPU"]
        repair_locs = ["REDACTED"]
        brands = ["ACE", "ALI", "ASU", "DEL", "GWY", "HEW", "LNV",
                  "MSS", "RCM", "RZR", "SAC", "SYC", "TSC"]

        if data["class"].upper().strip() not in classes: return False
        if data["brand"].upper().strip() not in brands: return False
        if data["labor_coverage"].upper().strip() not in coverage: return False

        return True

    def filter_data(parts):
        """
        Removes invalid elements from 'parts'.

        :param parts: List of part objects
        :return: A filtered list
        """
        return list(filter(lambda p: validate(p), parts))

    def hunter_task(popup, data, hunt_type):
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

        path = save_to_file(hunt_type, purge_subbed(filtered))
        popup.destroy()
        show_done(path)

    data = get_data(hunt_type)
    popup = tk.Toplevel()
    t = Thread(target=hunter_task, args=(popup,data,hunt_type))
    t.start()
