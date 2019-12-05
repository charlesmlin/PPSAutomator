from pathlib import Path
from tkinter import *
from tkinter import messagebox

from src.com.charlesmlin.pps_automator.util import Utils


class TkInput:
    _root: Tk
    _username_entry: Entry
    _password_entry: Entry
    _merchant_entry: Entry
    _payment_entry: Entry
    _submit_button: Button
    _username: str
    _password: str
    _merchant_code: int
    _payment_amount: float

    def __init__(self):
        self._username = ''
        self._password = ''
        self._merchant_code = 0
        self._payment_amount = 0.0
        self._root = Tk()
        self._root.winfo_toplevel().wm_title('PPS Automator')
        self._root.winfo_toplevel().wm_geometry('250x160')
        path: Path = Utils.get_project_path()
        if path is not None:
            self._root.wm_iconbitmap(path.joinpath('images', 'pps.ico'))
        Label(self._root, text='繳費靈戶口號碼', anchor=W).grid(row=0, sticky=W)
        self._username_entry = Entry(self._root)
        self._username_entry.grid(row=0, column=1)
        Label(self._root, text='戶口密碼', anchor=W).grid(row=1, sticky=W)
        self._password_entry = Entry(self._root, show="*")
        self._password_entry.grid(row=1, column=1)
        Label(self._root, text='商戶編號', anchor=W).grid(row=2, sticky=W)
        self._merchant_entry = Entry(self._root)
        self._merchant_entry.grid(row=2, column=1)
        Label(self._root, text='繳付費用', anchor=W).grid(row=3, sticky=W)
        self._payment_entry = Entry(self._root)
        self._payment_entry.grid(row=3, column=1)
        Label(self._root).grid(row=4)
        self._submit_button = Button(self._root, text='提交', command=self.submit)
        self._submit_button.grid(row=5, sticky=W)
        self._root.protocol("WM_DELETE_WINDOW", self.on_close)

    def submit(self) -> None:
        valid = True
        self._username = self._username_entry.get()
        if valid and len(self._username) <= 0:
            valid = False
            messagebox.showerror("錯誤", "繳費靈戶口號碼不應為空白")
        self._password = self._password_entry.get()
        if valid and len(self._password) <= 0:
            valid = False
            messagebox.showerror("錯誤", "戶口密碼不應為空白")
        try:
            self._merchant_code = getint(self._merchant_entry.get())
        except ValueError:
            if valid:
                valid = False
                messagebox.showerror("錯誤", "商戶編號應是一個數字")
        try:
            self._payment_amount = getdouble(self._payment_entry.get())
            if valid and self._payment_amount < 1:
                valid = False
                messagebox.showerror("錯誤", "最少繳交費用為 $1.00")
        except ValueError:
            if valid:
                valid = False
                messagebox.showerror("錯誤", "繳交費用應是一個數字")
        if valid:
            self._root.destroy()

    def on_close(self) -> None:
        if messagebox.askokcancel("確定離開", "你確定要離開？"):
            self._root.destroy()
            sys.exit()

    def show_front_end(self) -> None:
        self._root.mainloop()

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    def get_merchant_code(self) -> int:
        return self._merchant_code

    def get_payment_amount(self) -> float:
        return self._payment_amount
