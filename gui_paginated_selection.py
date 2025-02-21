import math
import tkinter as tk
from tkinter import font, messagebox


class PaginatedSelector:
    """
    A modal window that allows the user to select options from a given list,
    displaying them in pages with a fixed number of items per page and arranged in columns.
    """

    def __init__(self, parent, options, items_per_page=20, num_columns=3):
        self.root = tk.Toplevel(parent)
        self.root.title("Select Items")
        self.root.configure(bg="#f0f0f0")

        # Fonts for titles and buttons
        self.title_font = font.Font(family="Helvetica", size=10, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=9)

        self.all_options = options
        self.filtered_options = options.copy()
        self.num_columns = num_columns
        self.items_per_page = items_per_page
        self.current_page = 1
        self.selected_items = set()

        # Dictionary to maintain the state of the checkbuttons and associated
        # IntVars.
        self.checkbuttons = {}
        self.variables = {}

        self.update_total_pages()

        # Main frame with padding and border
        self.main_frame = tk.Frame(
            self.root, bg="#f0f0f0", relief=tk.RAISED, borderwidth=2
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Search frame
        self.search_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.search_frame.pack(fill=tk.X, pady=(10, 10))

        tk.Label(
            self.search_frame,
            text="Search:",
            font=self.title_font,
            bg="#f0f0f0").pack(
            side=tk.LEFT)

        self.search_entry = tk.Entry(
            self.search_frame,
            width=50,
            font=self.button_font,
            relief=tk.FLAT,
            bg="white",
        )
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_options)

        # Frame to hold the item buttons arranged in columns
        self.items_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.items_frame.pack(fill=tk.BOTH, expand=True)

        self.column_frames = []
        for i in range(num_columns):
            column_frame = tk.Frame(self.items_frame, bg="#f0f0f0")
            column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.column_frames.append(column_frame)

        # Pagination frame with navigation buttons
        self.pagination_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.pagination_frame.pack(fill=tk.X, pady=10)

        # Centered container for pagination buttons
        self.buttons_frame = tk.Frame(self.pagination_frame, bg="#f0f0f0")
        self.buttons_frame.pack(expand=True)

        self.prev_button = tk.Button(
            self.buttons_frame,
            text="Previous",
            font=self.button_font,
            command=self.prev_page,
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(
            self.buttons_frame,
            text="Next",
            font=self.button_font,
            command=self.next_page,
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Action frame for Accept/Cancel buttons
        self.actions_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.actions_frame.pack(fill=tk.X, pady=10)

        # Container for action buttons aligned to the right
        self.buttons_container = tk.Frame(self.actions_frame, bg="#f0f0f0")
        self.buttons_container.pack(side=tk.RIGHT, padx=5)

        self.accept_button = tk.Button(
            self.buttons_container,
            text="ACCEPT",
            font=self.button_font,
            command=self.accept,
        )
        self.accept_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(
            self.buttons_container,
            text="CANCEL",
            font=self.button_font,
            command=self.cancel,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # Initialize IntVar for each option
        for option in self.all_options:
            self.variables[option] = tk.IntVar()

        self.create_buttons()

    def update_total_pages(self):
        """Calculates the total number of pages based on the filtered options."""
        self.total_items = len(self.filtered_options)
        self.total_pages = math.ceil(self.total_items / self.items_per_page)

    def create_buttons(self):
        """
        Clears existing buttons and creates new checkbuttons for the options
        corresponding to the current page, distributing them evenly in columns.
        """
        # Clear previous buttons
        for col_frame in self.column_frames:
            for widget in col_frame.winfo_children():
                widget.destroy()

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = self.current_page * self.items_per_page
        page_options = self.filtered_options[start_index:end_index]

        if not page_options:
            return

        # Calculate number of rows dynamically based on the actual number of
        # options
        rows = math.ceil(len(page_options) / self.num_columns)

        # Iterate over each option and compute its position
        for index, option in enumerate(page_options):
            col = index // rows  # Determina la columna según el índice
            row = index % rows  # Determina la fila según el índice
            if option in self.selected_items:
                self.variables[option].set(1)
            check_button = tk.Checkbutton(
                self.column_frames[col],
                text=option,
                font=self.button_font,
                variable=self.variables[option],
                command=lambda option=option: self.select_option(option),
            )
            self.checkbuttons[option] = check_button
            # Ubica el botón en la fila calculada dentro de su columna
            check_button.grid(row=row, column=0, sticky="w", padx=10, pady=2)

    def select_option(self, option):
        """Toggles the selection state of an option."""
        if self.variables[option].get():
            self.selected_items.add(option)
        else:
            self.selected_items.discard(option)

    def prev_page(self):
        """Navigates to the previous page if available."""
        if self.current_page > 1:
            self.current_page -= 1
            self.create_buttons()

    def next_page(self):
        """Navigates to the next page if available."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.create_buttons()

    def filter_options(self, event):
        """
        Filters the available options based on the search query and
        resets the pagination.
        """
        query = self.search_entry.get().lower()
        if query:
            self.filtered_options = [
                option for option in self.all_options if query in option.lower()]
        else:
            self.filtered_options = self.all_options.copy()

        self.current_page = 1
        self.update_total_pages()
        self.create_buttons()

    def accept(self):
        """
        Displays a confirmation dialog with the selected options.
        If confirmed, the window is closed.
        """
        message = "Confirm the selection of the following items:\n\n"
        message += "\n".join(sorted(self.selected_items))

        if messagebox.askyesno("Confirm Selection", message):
            self.root.destroy()

    def cancel(self):
        """Closes the window without saving any selection."""
        self.root.destroy()


# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    sample_options = [f"Item {i}" for i in range(1, 101)]
    selector = PaginatedSelector(root, sample_options)
    root.mainloop()
