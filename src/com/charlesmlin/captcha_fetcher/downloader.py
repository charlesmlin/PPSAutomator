import hashlib
import os
import time
from functools import partial
from pathlib import Path
from tkinter import Tk, Entry, Label, Button, END
from typing import Tuple
from urllib.request import urlretrieve

from PIL import ImageTk, Image

from src.com.charlesmlin.pps_automator.util import Utils


def update_image(target: Path):
    img = ImageTk.PhotoImage(Image.open(str(target)))
    panel.configure(image=img)
    panel.image = img
    entry.delete(0, END)
    entry.focus_set()


def update_submission(counter: int, target: Path) -> None:
    partial_submit_func = partial(update_gui, counter + 1, target, True)
    submit_button.configure(command=partial_submit_func)
    root.bind('<Return>', lambda event: partial_submit_func())
    partial_next_func = partial(update_gui, counter, target, False)
    next_button.configure(command=partial_next_func)
    root.bind('<Escape>', lambda event: partial_next_func())
    partial_quit_func = partial(on_close, target)
    quit_button.configure(command=partial_quit_func)
    root.bind('<Control-c>', lambda event: on_close(target))
    root.protocol('WM_DELETE_WINDOW', lambda: on_close(target))


def update_gui(counter: int, original_path: Path = None, is_submit: bool = True):
    if original_path is not None:
        if is_submit:
            text: str = entry.get()
            text = text.upper()
            renamed_path: Path = original_path.parent.joinpath(f'{text}.jpg')
            os.rename(str(original_path), str(renamed_path))
        else:
            os.remove(str(original_path))
    new_path, img_link = get_new_image_path()
    print(f'Processing image #{counter}, link={img_link}, target={str(new_path)}')
    update_image(new_path)
    update_submission(counter, new_path)


def on_close(target: Path):
    os.remove(str(target))
    root.destroy()


def get_new_image_path() -> Tuple[Path, str]:
    milli = int(round(time.time() * 1000))
    md5_value = hashlib.md5(str(milli).encode('utf-8')).hexdigest()
    img_link = f'http://www.ppshk.com/pps/botdetectcaptcha?get=image&c=exampleCaptchaTag&t={md5_value}'
    path: Path = Utils.get_project_path()
    new_path = path.joinpath('captcha', f'{md5_value}.jpg')
    urlretrieve(img_link, str(new_path))
    return new_path, img_link


if __name__ == '__main__':
    root = Tk()
    panel = Label(root)
    panel.grid(row=0, columnspan=3)
    entry = Entry(root)
    entry.grid(row=1, columnspan=3)
    Label(root).grid(row=2)
    submit_button = Button(root, text='Submit (Enter)')
    submit_button.grid(row=3)
    next_button = Button(root, text='Next (Escape)')
    next_button.grid(row=3, column=1)
    quit_button = Button(root, text='Quit (Ctrl-C)')
    quit_button.grid(row=3, column=2)
    Label(root).grid(row=4)
    update_gui(1)
    root.mainloop()
