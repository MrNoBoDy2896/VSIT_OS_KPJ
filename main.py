from gui import *
import tkinter as tk
from tkinter import simpledialog
from client_api import ChatClient


def get_connection_settings():
    root = tk.Tk()
    root.withdraw()

    host = simpledialog.askstring(
        "Настройка подключения",
        "Введите IP адрес сервера:",
        initialvalue="localhost"
    )
    if host is None:  # Если нажата Cancel
        return None, None

    port = simpledialog.askinteger(
        "Настройка подключения",
        "Введите порт сервера:",
        initialvalue=8080,
        minvalue=1,
        maxvalue=65535
    )

    root.destroy()
    return host, port


if __name__ == "__main__":
    host, port = get_connection_settings()

    if host is None or port is None:
        print("Подключение отменено")
        exit()

    client.set_connection_params(host, port)

    root.mainloop()
