import logging
import os
import re
import tkinter as tk
from dataclasses import dataclass
from typing import ClassVar

from tkinter import filedialog, messagebox, simpledialog, ttk

from excel_parser import generate_formatted_names, load_excel_dataframe
from file_manager import get_file_paths_and_extension, rename_files

# Import updated modules
from gui_drag_and_drop import DragAndDropFixedInputs
from gui_paginated_selection import PaginatedSelector
from pdf_splitter import split_pdf

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="UTF-8",
    filename="batch_renamer.log",
)
logger = logging.getLogger(__name__)


@dataclass
class ApplicationDefaults:
    EXCEL: str = "No file selected"
    DIRECTORY: str = "No folder selected"
    VALID_EXTENSIONS: ClassVar[set] = {".xls", ".xlsx"}

class Application(tk.Frame):
    def __init__(self):
        # Initialize the main window and configure the interface
        self.root = tk.Tk()
        self.setup_main_window()
        self.initialize_variables()  # Initialize variables and styles
        super().__init__(self.root, bg=self.bg_main_color)
        self.main_frame = self
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.style.configure(
            "Custom.TButton",
            background=self.bg_button_main_color,
            foreground="white",
            activebackground=self.bg_button_main_color,
            activeforeground="white",
            padding=10,
            font=("Arial", 12, "bold"),
        )
        self.load_main_widgets()  # Load the main widgets in the interface
        self.add_progress_bar()  # Add the progress bar

    def setup_main_window(self):
        """Configures the main window parameters."""
        self.root.title("Batch File Renamer")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)

    def setup_styles(self):
        """Configures custom styles for the application."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.bg_main_color = "#f5f5f5"
        self.bg_button_main_color = "#2196f3"
        self.bg_font_color = "#212121"
        self.accent_color = "#1976d2"

    def initialize_variables(self):
        """Initializes variables and constants used in the application."""
        self.defaults = ApplicationDefaults()
        self.excel_file_path_default_value = self.defaults.EXCEL
        self.directory_default_value = self.defaults.DIRECTORY

        self.directory_path = tk.StringVar(value=self.directory_default_value)
        self.excel_file_path = tk.StringVar(
            value=self.excel_file_path_default_value)

        self.original_files_list = []  # List of original file paths
        self.dataframe = None  # DataFrame loaded from the Excel file
        self.new_names_list = []  # List to store new file names
        self.available_options = []  # Options available from the Excel file
        self.selected_options = []  # Options selected by the user
        self.extension_from_files = ""
        self.final_filename_format = tk.StringVar()
        self.current_page_index = 0
        self.pages = [self.stage_1, self.stage_2, self.stage_3, self.stage_4]
        self.setup_styles()

    def load_main_widgets(self):
        """Loads the main container, pager, and the first stage."""
        self.create_page_container()
        self.create_pager()
        self.pages[self.current_page_index]()

    def add_progress_bar(self):
        """Adds and configures a custom progress bar."""
        self.progress_var = tk.DoubleVar()

        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#E0E0E0",
            background=self.bg_button_main_color,
            bordercolor="#E0E0E0",
            lightcolor="#4CAF50",
            darkcolor="#388E3C",
        )

        self.progress = ttk.Progressbar(
            self.page_container,
            style="Custom.Horizontal.TProgressbar",
            variable=self.progress_var,
            maximum=len(self.pages),
            mode="determinate",
            length=300,
        )
        self.progress.grid(column=0, row=4, pady=10, sticky=tk.EW)
        self.update_progress()

    def update_progress(self):
        """Updates the progress bar based on the current stage."""
        self.progress_var.set(self.current_page_index + 1)

    def create_page_container(self):
        """Creates the main container for the different interface stages."""
        self.page_container = ttk.Frame(self.main_frame, padding="20")

        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(1, weight=1)
        self.page_container.grid(column=0, row=0, sticky=tk.NSEW)

        self.title = ttk.Label(
            self.page_container,
            font=("Arial", 24, "bold"),
            foreground=self.bg_font_color,
        )
        self.title.grid(column=0, row=0, pady=(0, 20))

        # Frame for content with border and shadow
        content_frame = ttk.Frame(self.page_container, style="Card.TFrame")
        content_frame.grid(column=0, row=1, sticky=tk.NSEW, pady=10)

        self.content = ttk.Label(
            content_frame, wraplength=700, font=("Arial", 14), padding=20
        )
        self.content.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(
            self.page_container, font=("Arial", 14), wraplength=700, padding=10
        )
        self.label.grid(column=0, row=2, sticky=tk.NSEW, pady=10)

        self.button = ttk.Button(
            self.page_container, style="Custom.TButton", cursor="hand2"
        )
        self.button.grid(column=0, row=3, sticky=tk.EW, pady=10)

    def create_pager(self):
        """Creates the pager with navigation buttons for different stages."""
        self.pager = ttk.Frame(self.main_frame, padding="10")
        self.pager.columnconfigure([0, 1, 2], weight=1)
        self.pager.grid(column=0, row=1, sticky=tk.EW)

        self.prev_button = ttk.Button(
            self.pager,
            text="Previous",
            style="Custom.TButton",
            state=tk.DISABLED,
            cursor="hand2",
            command=lambda: self.change_page(-1),
        )
        self.prev_button.grid(column=0, row=0)

        self.page_number = ttk.Label(
            self.pager,
            font=("Arial", 18),
            text=f"Stage {self.current_page_index + 1} of {len(self.pages)}",
        )
        self.page_number.grid(column=1, row=0)

        self.next_button = ttk.Button(
            self.pager,
            text="Next",
            style="Custom.TButton",
            state=tk.DISABLED,
            cursor="hand2",
            command=lambda: self.change_page(1),
        )
        self.next_button.grid(column=2, row=0)

    def change_page(self, direction):
        """
        Changes the current interface stage.

        Args:
            direction (int): Direction of page change (-1 for previous, 1 for next).
        """
        new_index = self.current_page_index + direction
        if 0 <= new_index < len(self.pages):
            self.current_page_index = new_index
            self.update_label()
            self.update_buttons()
            self.pages[self.current_page_index]()
            self.page_number.config(
                text=f"Stage {self.current_page_index + 1} of {len(self.pages)}"
            )
            self.update_progress()

    def update_buttons(self):
        """Updates the state of the 'Previous' and 'Next' buttons based on the current stage."""
        self.prev_button.config(state=self._get_prev_button_state())
        self.next_button.config(state=self._get_next_button_state())

    def _get_prev_button_state(self):
        """Determines if the 'Previous' button should be enabled."""
        return tk.NORMAL if self.current_page_index > 0 else tk.DISABLED

    def _get_next_button_state(self):
        """Determines if the 'Next' button should be enabled."""
        return tk.NORMAL if self.is_stage_ready() else tk.DISABLED

    def is_stage_ready(self):
        """
        Checks if the current stage meets the requirements to advance.

        Returns:
            bool: True if the current stage is ready to proceed, False otherwise.
        """
        stage_conditions = {
            0: lambda: self.directory_path.get() != self.directory_default_value
            and len(self.original_files_list) > 1,
            1: lambda: self.excel_file_path.get() != self.excel_file_path_default_value
            and bool(self.selected_options),
            2: lambda: bool(self.final_filename_format.get()),
            3: lambda: False,  # Final stage: no need to advance.
        }
        return stage_conditions.get(self.current_page_index, lambda: False)()

    def get_name_label(self):
        """
        Returns the descriptive text for the current stage.

        Returns:
            str: Descriptive text.
        """
        stage_labels = {
            0: self._get_directory_label,
            1: self._get_excel_label,
            2: self._get_format_label,
            3: self._get_summary_label,
        }
        return stage_labels.get(self.current_page_index, lambda: "")()

    def _get_excel_label(self):
        """Generates the label for the Excel file selection stage."""
        excel_path_value = "/".join(self.excel_file_path.get().split("/")[-2:])
        return (
            f"Selected file: .../{excel_path_value.lower()}"
            if excel_path_value != self.excel_file_path_default_value
            else self.excel_file_path_default_value
        )

    def _get_directory_label(self):
        """Generates the label for the folder selection stage."""
        folder_value = "/".join(self.directory_path.get().split("/")[-2:])
        if folder_value != self.directory_default_value:
            if self.original_files_list:
                return f"Selected folder: .../{
                    folder_value.lower()}\nFiles found: {
                    len(
                        self.original_files_list)}"
            else:
                return f"Selected folder: .../{folder_value.lower()}"
        else:
            return self.directory_default_value

    def _get_summary_label(self):
        """Generates the final summary text."""
        return self.generate_summary()

    def _get_format_label(self):
        """Generates the label text for the output format stage."""
        columns = (
            ", ".join(self.selected_options)
            if self.selected_options
            else "No columns selected"
        )
        final = (
            self.final_filename_format.get()
            if self.final_filename_format.get()
            else "No final name defined"
        )
        return f"Selected columns: {columns}\nFinal name: {final}"

    def update_label(self):
        """Updates the secondary label with the current stage's descriptive text."""
        self.label.config(text=self.get_name_label())

    def generate_summary(self):
        """
        Generates a summary of the collected information.

        Returns:
            str: Summary text including folder, base file, and output format.
        """
        return (
            f"• Folder: .../{'/'.join(self.directory_path.get().split('/')[-2:]).lower()}\n"
            f"• Base file: .../{'/'.join(self.excel_file_path.get().split('/')[-2:]).lower()}\n"
            f"• Output filename format: {self.final_filename_format.get()}\n"
        )

    def select_directory(self):
        """Allows the user to select and validate the working folder."""
        try:
            folder = filedialog.askdirectory(
                title="Select folder containing files to rename",
                parent=self.root)
            if not folder:
                return
            if not os.access(folder, os.W_OK):
                raise PermissionError(
                    "No write permission for the selected folder")
            self.directory_path.set(folder)
            self.update_label()
            self.update_buttons()
            logger.info(f"Folder selected: {folder}")
            messagebox.showinfo("Success", f"Folder selected:\n{folder}")
            self.load_original_names()
        except PermissionError as e:
            logger.error(f"Permission error: {str(e)}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error selecting folder: {str(e)}")
            messagebox.showerror("Error", f"Error selecting folder: {str(e)}")

    def select_excel_file(self):
        """Allows the user to select and validate an Excel file (.xls or .xlsx)."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Excel file (.xls or .xlsx)",
                parent=self.root,
                filetypes=[("Excel files", "*.xls *.xlsx"),
                           ("All files", "*.*")],
            )
            if not file_path:
                return
            _, ext = os.path.splitext(file_path.lower())
            if ext not in ApplicationDefaults.VALID_EXTENSIONS:
                valid_ext_str = ", ".join(
                    sorted(ApplicationDefaults.VALID_EXTENSIONS))
                messagebox.showerror(
                    "Invalid File",
                    f"Selected file is not valid.\nPlease choose a file with one of the following extensions: {valid_ext_str}",
                )
                return
            if not os.access(file_path, os.R_OK):
                raise PermissionError(
                    "No read permission for the selected file")
            self.excel_file_path.set(file_path)
            self.update_label()
            self.update_buttons()
            logger.info(f"Excel file selected: {file_path}")
            messagebox.showinfo(
                "Success", f"Excel file selected:\n{file_path}")
            self.load_dataframe()
        except Exception as e:
            logger.error(f"Error selecting Excel file: {str(e)}")
            messagebox.showerror(
                "Error", f"Error selecting Excel file:\n{str(e)}")

    def load_original_names(self):
        """
        Loads the original file paths from the selected folder.
        If a single PDF is found, prompts the user to split it.
        """
        try:
            self._set_loading_state("Loading files...", True)
            self.root.update()
            self.original_files_list, self.extension_from_files = (
                get_file_paths_and_extension(self.directory_path.get())
            )
            if (
                len(self.original_files_list) == 1
                and self.extension_from_files.lower() == ".pdf"
            ):
                split_confirm = messagebox.askokcancel(
                    "Split PDF",
                    "A single PDF file was found.\nDo you want to split it?",
                )
                if split_confirm:
                    pages_per_chunk = simpledialog.askinteger(
                        "Split PDF",
                        "Enter number of pages per file:",
                        parent=self.root,
                        minvalue=1,
                        initialvalue=1,
                    )
                    if pages_per_chunk is not None:
                        output_folder = os.path.join(
                            self.directory_path.get(), "split")
                        self.directory_path.set(output_folder)
                        success = split_pdf(
                            self.original_files_list[0],
                            self.directory_path.get(),
                            pages_per_chunk,
                        )
                        if success:
                            messagebox.showinfo(
                                "Split Completed", "The PDF was split successfully.")
                            self.load_original_names()
                            return
                        else:
                            messagebox.showwarning(
                                "Split", "Could not split the file.")
                            return
                else:
                    self.directory_path.set(self.directory_default_value)
                    self.original_files_list = []
                    self.extension_from_files = ""
                    messagebox.showerror(
                        "Error", "The PDF was not split. Cannot process a single file.")
                    self._set_loading_state("Select folder", False)
                    return
            if self.original_files_list and self.extension_from_files:
                self.extension_from_files = os.path.splitext(
                    self.original_files_list[0]
                )[1]
                self._set_loading_state("Select items", False)
                self.button.config(text="Change folder",
                                   command=self.select_directory)
                self.update_label()
                self.update_buttons()
                messagebox.showinfo(
                    "Success", f"{len(self.original_files_list)} files found"
                )
            else:
                self._set_loading_state("Load files", False)
                self.button.config(text="Load files",
                                   command=self.load_original_names)
        except Exception as e:
            self._set_loading_state("Load files", False)
            messagebox.showerror("Error", f"Error loading files: {str(e)}")

    def load_dataframe(self):
        """Loads the DataFrame and available options from the selected Excel file."""
        try:
            self._set_loading_state("Loading file...", True)
            self.root.update()
            self.dataframe, self.available_options = load_excel_dataframe(
                self.excel_file_path.get()
            )
            if self.available_options and not self.dataframe.empty:
                self._set_loading_state("Select columns", False)
                self.button.config(command=self.show_item_selector)
            else:
                self._set_loading_state("Load file", False)
        except Exception as e:
            self._set_loading_state("Load file", False)
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def show_item_selector(self):
        """Displays the selector for Excel options."""
        selector = PaginatedSelector(self.root, self.available_options)
        self.root.wait_window(selector.root)
        self._process_selection(selector)

    def show_filename_selector(self):
        """Displays the drag and drop window to define the output filename format."""
        selector = DragAndDropFixedInputs(
            self.root, self.selected_options, self.extension_from_files
        )
        self.root.wait_window(selector.root)
        self._process_drag_and_drop(selector)

    def _process_selection(self, selector):
        """Processes the options selected by the user."""
        self.selected_options = list(selector.selected_items)
        if self.selected_options:
            self._handle_successful_selection()
        else:
            messagebox.showinfo("Info", "No items selected")
        self.update_label()
        self.update_buttons()

    def _process_drag_and_drop(self, selector):
        """Processes the filename format selected by the user."""
        if selector.final_filename:
            self.final_filename_format.set(selector.final_filename)
            logger.info(f"Selected filename format: {selector.final_filename}")
        else:
            self.final_filename_format.set("")
            messagebox.showinfo("Info", "No filename defined")
        self.update_label()
        self.update_buttons()

    def _handle_successful_selection(self):
        """Shows an informational message upon successful selection."""
        num_items = len(self.selected_options)
        logger.info(f"Selected items: {self.selected_options}")
        messagebox.showinfo("Success", f"{num_items} items selected")

    def _set_loading_state(self, text, is_loading):
        """Configures the interface state during loading processes."""
        cursor = "wait" if is_loading else ""
        state = "disabled" if is_loading else "normal"
        self.root.config(cursor=cursor)
        self.button.config(text=text, state=state)

    def stage_1(self):
        """Stage 1: Folder selection."""
        self.title.config(text="Select Folder to Process")
        self.content.config(
            text="Select the folder containing the files to rename.\nNote: Only PDF files are supported.")
        self.update_label()
        self.button.config(
            text=f"{
                'Change' if self.original_files_list else 'Select'} folder",
            command=self.select_directory,
        )

    def stage_2(self):
        """Stage 2: Excel file selection and column selection."""
        self.title.config(text="Select Excel File")
        self.content.config(
            text="Select the Excel file to use as a base.\nOnly .xls or .xlsx files are accepted.\nThen, select the desired columns.")
        self.update_label()
        self.button.config(
            text=f"{
                'Change' if self.excel_file_path.get() != self.excel_file_path_default_value else 'Select'} file",
            command=self.select_excel_file,
        )

    def stage_3(self):
        """Stage 3: Define output filename format."""
        self.title.config(text="Define Output Format")
        self.update_label()
        self.button.config(
            text="Select output format", command=self.show_filename_selector
        )

    def stage_4(self):
        """Stage 4: Final summary and confirmation."""
        self.title.config(text="Summary and Confirmation")
        self.content.config(
            text="Review the final information and click 'Start renaming files'.")
        self.update_label()
        self.button.config(text="Start renaming files",
                           command=self.start_renaming)

    def start_renaming(self):
        """Loads new filenames, validates, and renames the files."""
        try:
            self._set_loading_state("Renaming files...", True)
            self.root.update()
            missing_columns = [
                col
                for col in self.selected_options
                if col not in self.dataframe.columns
            ]
            if missing_columns:
                messagebox.showerror(
                    "Error", f"The following columns were not found in the Excel file: {
                        ', '.join(missing_columns)}", )
                self._set_loading_state("Rename files", False)
                return
            format_str = self.final_filename_format.get()
            if not re.match(r"^[\w\-. ]+$", format_str):
                messagebox.showerror(
                    "Error", "The filename format contains invalid characters."
                )
                self._set_loading_state("Rename files", False)
                return
            self.new_names_list = generate_formatted_names(
                self.dataframe, self.selected_options, format_str
            )
            if not self.new_names_list:
                messagebox.showerror(
                    "Error", "Could not generate new file names.")
                self._set_loading_state("Rename files", False)
                return
            rename_files(self.original_files_list, self.new_names_list)
            self._set_loading_state("Renaming completed", False)
            messagebox.showinfo("Success", "Files renamed successfully.")
        except Exception as e:
            self._set_loading_state("Start renaming", False)
            messagebox.showerror("Error", f"Error renaming files: {str(e)}")


if __name__ == "__main__":
    app = Application()
    app.root.mainloop()
