import tkinter as tk
import subprocess
from playsound import playsound
from tkinter import Text


def get_game_size():
    root.after(5000, retrieve_window_size)


def retrieve_window_size():
    global label_info
    output = subprocess.check_output(["python", "window_size.py"]).decode("utf-8")
    update_text_info(output)
    playsound("sound.wav")


def run_script_delayed():
    root.after(10000, run_script)


def run_script():
    subprocess.call(["python", "aim_math.py"])


root = tk.Tk()
root.title("Автоприцел v0.1")
root.geometry("320x250")
root.resizable(False, False)

label = tk.Label(root, text="Выберите действие:")
label.pack(pady=10)

get_size_button = tk.Button(root, text="Получить размеры окна игры", command=get_game_size)
get_size_button.pack(pady=5)

run_script_button = tk.Button(root, text="Запустить скрипт", command=run_script)
run_script_button.pack(pady=5)

text_info = Text(root, height=3, width=40)
text_info.pack(pady=10)


def update_text_info(output):
    text_info.delete(1.0, tk.END)
    text_info.insert(tk.END, output)


update_text_info("{Координаты окна}")

root.mainloop()
