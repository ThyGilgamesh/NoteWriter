import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os
import json


def save_subjects(subjects):
    with open("subjects.json", "w") as subjects_file:
        json.dump(subjects, subjects_file)


def load_subjects():
    try:
        with open("subjects.json", "r") as subjects_file:
            return json.load(subjects_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


subject_folder_names = load_subjects()


class SubjectDialog(tk.simpledialog.Dialog):
    def body(self, master: tk.Tk) -> tk.Frame:

        tk.Label(master, text="Summary:     ").grid(row=0, column=0)
        tk.Label(master, text="Subject: ").grid(row=1, column=0)

        self.summary_var: tk.StringVar = tk.StringVar()
        self.summary_entry: tk.Entry = tk.Entry(master, textvariable=self.summary_var)
        self.summary_entry.grid(row=0, column=1)

        self.subject_var: tk.StringVar = tk.StringVar()
        self.subject_var.set("No Subject")

        subjects = load_subjects()

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
        font_style = ("Source Code Pro", 11)
        dateAndTime: str = datetime.now().strftime("%Y/%m/%d %H:%M")
        self.root: tk.Tk = root
        self.root.title(f"Note Writer - {dateAndTime}")
        self.text_widget: tk.Text = tk.Text(root, wrap="word", undo=True, bg="gray", fg="white")
        self.text_widget.configure(font=font_style)
        self.text_widget.pack(expand=True, fill="both")
        self.file_path: str | None
        self.autofolder: tk.BooleanVar = tk.BooleanVar(value=True)
        self.subjects_menu: tk.Menu = tk.Menu(root)
        self.update_subjects_menu()
        self.subject_folder_names = load_subjects()
        self.subjects_menu: tk.Menu = tk.Menu(root)
        self.update_subjects_menu()

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

        edit_menu.add_command(label="Insert Date and Time", command=self.writeDateTime,
                              accelerator="Ctrl+Shift+D")

        edit_menu.add_command(label="Manage Subjects", command=self.manage_subjects)

        self.autofolder_label: tk.Label = tk.Label(root, text="Ctrl+Q to toggle Auto Folder",
                                                   anchor="e", padx=5)
        self.autofolder_label.pack(side="bottom", fill="x")

        root.bind("<Control-n>", lambda event: self.new_file())
        root.bind("<Control-o>", lambda event: self.open_file())
        root.bind("<Control-s>", lambda event: self.save_file())
        root.bind("<Control-S>", lambda event: self.save_as_file())
        root.bind("<Control-f>", lambda event: self.find_text())
        root.bind("<Control-q>", lambda event: self.toggle_autofolder())
        root.bind("<Control-D>", lambda event: self.writeDateTime())

        root.protocol("WM_DELETE_WINDOW", self.on_exit)

        edit_menu.add_separator()
        edit_menu.add_command(label="Set Default Folder", command=self.set_default_folder)

    def writeDateTime(self) -> None:
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S ")
        self.text_widget.insert(tk.INSERT, current_time)

    def manage_subjects(self) -> None:
        ManageSubjectsDialog(self.root, self.subject_folder_names)
        self.update_subjects_menu()

    def update_subjects_menu(self) -> None:
        self.subjects_menu.delete(0, tk.END)

        for subject in subject_folder_names:
            self.subjects_menu.add_command(label=subject,
                                           command=lambda s=subject: self.select_subject(s))

    def set_default_folder(self) -> None:
        default_folder = filedialog.askdirectory(title="Select Default Folder")
        if default_folder:
            settings = {'default_folder': default_folder}
            with open("settings.json", "w") as settings_file:
                json.dump(settings, settings_file)

    def get_default_folder(self) -> str | None:
        try:
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                return settings.get('default_folder', None)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

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

        if self.autofolder.get():
            file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                   filetypes=[("Text Documents", "*.txt"),
                                                              ("All Files", "*.*")])
        else:
            default_folder = self.get_default_folder()
            file_path = tk.filedialog.askopenfilename(initialdir=default_folder,
                                                      defaultextension=".txt",
                                                      filetypes=[("Text Documents", "*.txt"),
                                                                 ("All Files", "*.*")])

        if file_path:
            self.file_path = file_path
            self.text_widget.delete(1.0, tk.END)
            self.load_large_file(file_path)

    def load_large_file(self, file_path: str) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    self.text_widget.insert(tk.END, line)
                    self.text_widget.update_idletasks()
        except Exception as e:
            print(f"Error loading file: {e}")

    def save_file(self, event=None):
        if not hasattr(self, 'file_path') or not self.file_path:
            self.save_as_file()
        else:
            content = self.text_widget.get(1.0, tk.END)
            with open(self.file_path, "w") as file:
                file.write(content)

    def save_as_file(self, event=None) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
        file_path = None

        if self.autofolder.get():
            subject_dialog = SubjectDialog(self.root)
            subject = subject_dialog.result

            if subject is None:
                pass

            else:
                suggested_name = f"{current_time} {subject['summary']}.txt"
                default_folder = self.get_default_folder()

                base_directory = default_folder

                saveDirectory = os.path.join(base_directory, f'{subject["subject"]}')
                os.makedirs(saveDirectory, exist_ok=True)
                file_path = os.path.join(saveDirectory, suggested_name)
        else:
            summary = tk.simpledialog.askstring("Summary", "Enter summary: ", parent=self.root)

            if not summary:
                summary = ''

            suggested_name = f"Note {current_time} {summary}.txt"
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


class ManageSubjectsDialog(tk.simpledialog.Dialog):
    def __init__(self, root: tk.Tk, subject_folder_names: list[str]) -> None:
        self.subject_folder_names = subject_folder_names
        self.root: tk.Tk = root
        super().__init__(root)

    def body(self, master: tk.Tk) -> tk.Frame:
        tk.Label(master, text="Manage Subjects").grid(row=0,
                                                      column=0,
                                                      columnspan=2,
                                                      pady=10)

        self.subject_listbox: tk.Listbox = tk.Listbox(master,
                                                      selectmode=tk.MULTIPLE)
        for subject in self.subject_folder_names:
            self.subject_listbox.insert(tk.END, subject)
        self.subject_listbox.grid(row=1, column=0, columnspan=2, pady=10)

        add_button = tk.Button(master, text="Add", command=self.add_subject)
        add_button.grid(row=2, column=0, padx=5, pady=5)

        remove_button = tk.Button(master, text="Remove",
                                  command=self.remove_subject)
        remove_button.grid(row=2, column=1, padx=5, pady=5)

    def apply(self) -> None:
        save_subjects(self.subject_folder_names)

    def add_subject(self) -> None:
        new_subject = tk.simpledialog.askstring("Add Subject", "Enter the new subject:",
                                                parent=self.root)
        if new_subject and new_subject not in self.subject_folder_names:
            self.subject_folder_names.append(new_subject)
            self.subject_listbox.insert(tk.END, new_subject)

    def remove_subject(self) -> None:
        selected_indices = self.subject_listbox.curselection()
        for index in reversed(selected_indices):
            removed_subject = self.subject_listbox.get(index)
            self.subject_folder_names.remove(removed_subject)
            self.subject_listbox.delete(index)


if __name__ == "__main__":
    root = tk.Tk()
    text_editor = TextEditor(root)
    root.mainloop()
