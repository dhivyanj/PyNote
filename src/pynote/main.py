# src/pynote/main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import utils

APP_TITLE = "PyNote"

class PyNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('800x600')
        self._filepath = None
        self._encoding = 'utf-8'
        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()

    def _create_widgets(self):
        # Text widget with scrollbar
        self.text = tk.Text(self, wrap='word', undo=True)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)

        # status bar
        self.status = tk.StringVar()
        self.status.set(f'Ln 1, Col 0\nEncoding: {self._encoding}')
        status_bar = ttk.Label(self, textvariable=self.status, anchor='w')
        status_bar.pack(side='bottom', fill='x')

        # update cursor position
        self.text.bind('<KeyRelease>', self._update_status)
        self.text.bind('<ButtonRelease>', self._update_status)

    def _create_menu(self):
        menu = tk.Menu(self)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label='New', command=self.new_file)
        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.add_command(label='Save As', command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label='Set Encoding', command=self.set_encoding)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        menu.add_cascade(label='File', menu=filemenu)
        self.config(menu=menu)

    def _bind_shortcuts(self):
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-e>', lambda e: self.set_encoding())
        self.bind('<Control-z>', lambda e: self.text.event_generate('<<Undo>>'))
        self.bind('<Control-y>', lambda e: self.text.event_generate('<<Redo>>'))

    def new_file(self):
        if self._confirm_discard():
            self.text.delete('1.0', tk.END)
            self._filepath = None
            self._encoding = 'utf-8'
            self.title(APP_TITLE)
            self._update_status()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                self._encoding = utils.detect_encoding(path)
            except Exception:
                self._encoding = 'utf-8'
            try:
                with open(path, 'r', encoding=self._encoding) as f:
                    data = f.read()
                self.text.delete('1.0', tk.END)
                self.text.insert('1.0', data)
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self._update_status()
            except Exception as e:
                old_enc = self._encoding
                try:
                    self._encoding = 'utf-8'
                    with open(path, 'r', encoding='utf-8') as f:
                        data = f.read()
                    self.text.delete('1.0', tk.END)
                    self.text.insert('1.0', data)
                    self._filepath = path
                    self.title(f"{APP_TITLE} - {path}")
                    self._update_status()
                except Exception:
                    self._encoding = old_enc or 'utf-8'
                    messagebox.showerror('Error', f'Failed to open file: {str(e)}')

    def save_file(self):
        if self._filepath:
            try:
                enc = self._encoding or 'utf-8'
                with open(self._filepath, 'w', encoding=enc) as f:
                    f.write(self.text.get('1.0', tk.END))
                self._encoding = enc
                self.text.edit_modified(False)
                self._update_status()
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                enc = self._encoding or 'utf-8'
                with open(path, 'w', encoding=enc) as f:
                    f.write(self.text.get('1.0', tk.END))
                self._filepath = path
                self._encoding = enc
                self.title(f"{APP_TITLE} - {path}")
                self.text.edit_modified(False)
                self._update_status()
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')

    def _update_status(self, event=None):
        idx = self.text.index(tk.INSERT).split('.')
        line = idx[0]
        col = idx[1]
        if self._encoding:
            self.status.set(f'Ln {line}, Col {col}\nEncoding: {self._encoding}')
        else:
            self.status.set(f'Ln {line}, Col {col}\nEncoding: -')

    def set_encoding(self):
        dialog = tk.Toplevel(self)
        dialog.title('Set Encoding')
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text='Select file encoding:').pack(padx=10, pady=(10, 0))
        enc_var = tk.StringVar(value=self._encoding or 'utf-8')
        cb = ttk.Combobox(dialog, textvariable=enc_var, values=['utf-8', 'latin-1'], state='readonly')
        cb.pack(padx=10, pady=10)
        cb.focus_set()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(padx=10, pady=(0, 10))

        def on_ok():
            self._encoding = enc_var.get()
            if self._filepath:
                try:
                    with open(self._filepath, 'r', encoding=self._encoding) as f:
                        data = f.read()
                    self.text.delete('1.0', tk.END)
                    self.text.insert('1.0', data)
                except Exception as e:
                    messagebox.showerror('Error', f'Failed to reload file with encoding {self._encoding}: {e}')
                else:
                    self._encoding = enc_var.get()
            self._update_status()
            dialog.destroy()            

        def on_cancel():
            dialog.destroy()

        ttk.Button(btn_frame, text='OK', command=on_ok).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Cancel', command=on_cancel).pack(side='left', padx=5)

        self.wait_window(dialog)

    def _confirm_discard(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel(
                'Unsaved changes',
                'You have unsaved changes. Save before continuing?'
            )
            if resp is None:
                return False
            if resp:
                self.save_file()
        return True


if __name__ == '__main__':
    app = PyNoteApp()
    app.mainloop()

