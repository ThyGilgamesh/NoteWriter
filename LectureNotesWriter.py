import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os


class SubjectDialog(tk.simpledialog.Dialog):
    def body(self, master: tk.Tk) -> tk.Frame:
        tk.Label(master, text="SUMMARY:").grid(row=0, column=0)
        tk.Label(master, text="SUBJECT:").grid(row=1, column=0)

        self.summary_var: tk.StringVar = tk.StringVar()
        self.summary_entry: tk.Entry = tk.Entry(master, textvariable=self.summary_var)
        self.summary_entry.grid(row=0, column=1)

        self.subject_var: tk.StringVar = tk.StringVar()
        self.subject_var.set("No Subject")

        subjects = ['Optics', 'Quantum', 'Math 3B']

        self.subject_dropdown: tk.OptionMenu = tk.OptionMenu(master, self.subject_var, *subjects)
        self.subject_dropdown.grid(row=1, column=1)

    def apply(self) -> None:
        self.result = {'summary': self.summary_var.get(), 'subject': self.subject_var.get()}

    def buttonbox(self) -> None:
        box = tk.Frame(self)

        w = tk.Button(box, text="Save", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Continue Without Saving", width=20, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()


class TextEditor:
    def __init__(self, root: tk.Tk) -> None:
        dateAndTime: str = datetime.now().strftime("%Y %m %d %H%M")
        self.root: tk.Tk = root
        self.root.title(f"Lecture Notes - {dateAndTime}")
        self.text_widget: tk.Text = tk.Text(root, wrap="word", undo=True, bg="gray", fg="white")
        self.text_widget.configure(font=("Source Code Pro", 11))
        self.text_widget.pack(expand=True, fill="both")
        self.file_path: str | None
        self.autofolder: tk.BooleanVar = tk.BooleanVar(value=True)

        menu_bar: tk.Menu = tk.Menu(root)
        root.config(menu=menu_bar)

        file_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As",
                              command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit Without Saving", command=root.destroy)

        edit_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")

        self.autofolder_label: tk.Label = tk.Label(root, text="Ctrl+Q to toggle Auto Folder",
                                                   anchor="e", padx=5)
        self.autofolder_label.pack(side="bottom", fill="x")

        root.bind("<Control-n>", lambda event: self.new_file())
        root.bind("<Control-o>", lambda event: self.open_file())
        root.bind("<Control-s>", lambda event: self.save_file())
        root.bind("<Control-S>", lambda event: self.save_as_file())
        root.bind("<Control-f>", lambda event: self.find_text())
        root.bind("<Control-q>", lambda event: self.toggle_autofolder())

        root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def toggle_autofolder(self) -> None:
        self.autofolder.set(not self.autofolder.get())
        self.update_autofolder_label()

    def update_autofolder_label(self) -> None:
        current_state = "On" if self.autofolder.get() else "Off"
        self.autofolder_label.config(text=f"Auto Folder is {current_state}")

    def on_exit(self) -> None:
        self.save_file()
        self.root.destroy()

    def new_file(self, event: tk.Event | None = None) -> None:
        self.save_file()
        self.text_widget.delete(1.0, tk.END)
        self.file_path = None

    def open_file(self, event: tk.Event | None = None) -> None:
        self.save_file()

        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                               filetypes=[("Text Documents", "*.txt"),
                                                          ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
            self.file_path = file_path

    def save_file(self, event: tk.Event | None = None) -> None:
        if not hasattr(self, 'file_path') or not self.file_path:
            self.save_as_file()
        else:
            content = self.text_widget.get(1.0, tk.END)
            with open(self.file_path, "w") as file:
                file.write(content)

    def save_as_file(self, event: tk.Event | None = None) -> None:
        subject_dialog = SubjectDialog(self.root)
        subject = subject_dialog.result

        if subject is None:
            pass
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
            suggested_name = f"{subject['subject']} {current_time} {subject['summary']}.txt"
            if self.autofolder.get():
                base_directory = r"C:\Users\bigre\OneDrive\Documents\Assignments\Lecture Notes"
                saveDirectory = os.path.join(base_directory, f'{subject["subject"]}')
                os.makedirs(saveDirectory, exist_ok=True)
                file_path = os.path.join(saveDirectory, suggested_name)
            else:
                file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt",
                                                            initialfile=suggested_name,
                                                            filetypes=[("Text Documents", "*.txt"),
                                                                       ("All Files", "*.*")])
            if file_path:
                content = self.text_widget.get(1.0, tk.END)
                with open(file_path, "w") as file:
                    file.write(content)
                self.file_path = file_path

    def find_text(self, event: tk.Event | None = None) -> None:
        target = tk.simpledialog.askstring("Find", "Enter text to find:")
        if target:
            start_index = self.text_widget.search(target, "1.0", tk.END, nocase=True)
            while start_index:
                end_index = f"{start_index}+{len(target)}c"
                self.text_widget.tag_add(tk.SEL, start_index, end_index)
                start_index = self.text_widget.search(target, end_index, tk.END, nocase=True)

            if self.text_widget.tag_ranges(tk.SEL):
                self.text_widget.mark_set(tk.INSERT, self.text_widget.tag_ranges(tk.SEL)[0])
                self.text_widget.see(tk.INSERT)
                self.text_widget.tag_configure(tk.SEL, background="white", foreground="black")


if __name__ == "__main__":
    root = tk.Tk()
    text_editor = TextEditor(root)
    root.mainloop()