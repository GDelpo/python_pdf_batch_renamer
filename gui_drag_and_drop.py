import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox

# Set of allowed characters for inputs.
ALLOWED_CHARS = "-_,; "

CELL_WIDTH = 120  # Fixed width for each column


class DraggableLabel(tk.Label):
    def __init__(self, master, controller, text, pair_index, font, **kwargs):
        """
        Args:
            master: The container widget for the label (used for layout).
            controller: Instance that contains the reorder_label method.
            text (str): Text to display.
            pair_index (int): Index of the associated input.
            font: Font to use.
        """
        super().__init__(master, text=text, bg="#f0f0f0", width=10, font=font, **kwargs)
        self.controller = (
            # Reference to the controller with reorder_label method.
            controller
        )
        self.pair_index = pair_index
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self._drag_data = {"x": 0}

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self.lift()  # Bring the label to the front while dragging.
        self.grid_forget()  # Remove the label from the grid for free movement.

    def do_drag(self, event):
        dx = event.x - self._drag_data["x"]
        new_x = self.winfo_x() + dx
        # Move the label along the X-axis (keeping Y coordinate at 0).
        self.place(x=new_x, y=0)

    def stop_drag(self, event):
        drop_x = self.winfo_x()
        self.place_forget()  # Remove absolute positioning.
        # Call the controller's reorder_label method.
        self.controller.reorder_label(self, drop_x)


class DragAndDropFixedInputs:
    def __init__(self, parent, words, extension, **kwargs):
        # Create a Toplevel window to have a modal-like interface.
        self.root = tk.Toplevel(parent)
        self.root.title("Define Output Format")
        self.root.configure(bg="#f0f0f0")

        # Main frame within the Toplevel window.
        self.frame = tk.Frame(self.root, bg="#f0f0f0", **kwargs)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.cell_width = CELL_WIDTH
        self.extension = extension if extension.startswith(
            ".") else "." + extension
        self.labels = []  # List of draggable labels.
        self.entries = (
            []
        )  # List of fixed input fields (one less than the number of labels).
        self.final_filename = None  # Variable to store the final filename.

        # Fonts for titles and buttons.
        self.title_font = tkFont.Font(
            family="Helvetica", size=10, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=9)

        # Calculate total number of columns:
        #   - For N words, we create N labels, but only N-1 entries.
        #   - Total columns: 2*(N-1) for (label+entry) pairs, + 1 for the last label, + 1 for the extension.
        #   - This results in 2*N columns.
        total_cols = len(words) * 2

        for i in range(total_cols):
            self.frame.grid_columnconfigure(i, minsize=self.cell_width)

        # Register the validation function for the inputs.
        vcmd = self.root.register(self.validate_input)

        # --- Nueva organización: colocar la etiqueta de caracteres permitidos en la parte superior ---
        self.allowed_chars_label = tk.Label(
            self.frame,
            text=f"Allowed characters: {ALLOWED_CHARS}",
            bg="#f0f0f0",
            font=self.button_font,
        )
        self.allowed_chars_label.grid(
            row=0, column=0, columnspan=total_cols, pady=(10, 5)
        )

        # Place draggable labels and entries in the next row (row 1).
        for i, word in enumerate(words):
            # Create the draggable label.
            label = DraggableLabel(
                self.frame, self, word, pair_index=i, font=self.title_font
            )
            label.grid(row=1, column=i * 2, padx=5, pady=5)
            self.labels.append(label)

            # Create an Entry only for the first (N-1) words.
            if i < len(words) - 1:
                entry = tk.Entry(
                    self.frame,
                    validate="key",
                    validatecommand=(vcmd, "%P"),
                    font=self.button_font,
                    relief=tk.FLAT,
                    bg="white",
                )
                entry.grid(row=1, column=i * 2 + 1, padx=5, pady=5)
                self.entries.append(entry)

        # Place the extension label in the last column of row 1.
        self.extension_label = tk.Label(
            self.frame,
            text=self.extension,
            bg="lightgrey",
            width=10,
            font=self.title_font,
        )
        self.extension_label.grid(row=1, column=total_cols - 1, padx=5, pady=5)

        # "Accept" button in the next row (row 2).
        self.accept_button = tk.Button(
            self.frame,
            text="Aceptar",
            command=self.on_accept,
            font=self.button_font)
        self.accept_button.grid(
            row=2, column=0, columnspan=total_cols, pady=10)

    def validate_input(self, new_value):
        """Validates that the input contains only allowed characters."""
        if new_value == "":
            return True
        for ch in new_value:
            if ch not in ALLOWED_CHARS:
                return False
        return True

    def reorder_label(self, label, drop_x):
        """
        Reorders the draggable labels based on the final x-coordinate after dragging.

        Args:
            label: The label widget being dragged.
            drop_x: The x-coordinate where the label was dropped.
        """
        target_index = round(drop_x / (self.cell_width * 2))
        target_index = max(0, min(target_index, len(self.labels) - 1))
        if label in self.labels:
            self.labels.remove(label)
        self.labels.insert(target_index, label)
        # Update the grid position for each label.
        for i, lbl in enumerate(self.labels):
            lbl.grid_forget()
            lbl.grid(row=1, column=i * 2, padx=5, pady=5)

    def build_filename(self):
        """
        Constructs the final filename by interleaving the label texts (in their current order)
        with the corresponding entry text (if available). The file extension is appended at the end.
        """
        filename = ""
        for i, label in enumerate(self.labels):
            label_text = label.cget("text")
            entry_text = self.entries[i].get() if i < len(self.entries) else ""
            filename += label_text + entry_text
        filename += self.extension
        return filename

    def on_accept(self):
        """
        Handles the accept action. Builds the final filename, requests confirmation,
        and if confirmed, saves the filename and closes the window.
        """
        final_name = self.build_filename()
        if messagebox.askyesno(
            "Confirmation", f"Do you want to save the filename:\n{final_name}?"
        ):
            self.final_filename = final_name
            messagebox.showinfo("Saved", f"Filename saved:\n{final_name}")
            self.root.destroy()
        else:
            messagebox.showinfo("Cancelled", "Operation cancelled.")


# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Drag and Drop Test")
    root.configure(bg="#f0f0f0")

    # Example with 3 words: creates 3 labels but only 2 entries.
    words = ["One", "Two", "Three"]
    extension = ".pdf"

    selector = DragAndDropFixedInputs(root, words, extension)
    root.wait_window(selector.root)

    print("Final filename:", selector.final_filename)
