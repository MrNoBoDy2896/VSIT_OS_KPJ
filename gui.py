from logging import Logger
from tkinter import *
from db import *

from db import add_user

root = Tk()
root.title("Enigma Chat")
root.geometry("600x300")
#root.iconbitmap("путь к файлу иконки")
#/////////////////////////////////Регистрация и вход///////////////////////////////////////
login_enter_label = Label(root, text="Логин", font=("Comic Sans MS", 20))
password_enter_label = Label(root, text="Пароль", font=("Comic Sans MS", 20))

login_enter_entry = Entry(root, font=("Comic Sans MS", 20))
password_enter_entry = Entry(root, font=("Comic Sans MS", 20))


def gui_reg():
    password = password_enter_entry.get()
    login = login_enter_entry.get()
    add_user(login, password)

    login_enter_label.place_forget()
    password_enter_label.place_forget()
    login_enter_entry.place_forget()
    password_enter_entry.place_forget()
    reg_enter_button.place_forget()

def gui_log_in():
    password = password_enter_entry.get()
    login = login_enter_entry.get()
    print(log_in(login, password))

reg_enter_button = Button(root, text="Зарегистрироваться", font=("Comic Sans MS", 20), command=gui_reg)
log_in_enter_button = Button(root, text="Войти", font=("Comic Sans MS", 20), command=gui_log_in)


def reg_window():
    reg_button.place_forget()
    log_in_button.place_forget()

    title_lable.config(text = "Регистрация")

    login_enter_label.place(relx=0.1 , rely=0.3)
    password_enter_label.place(relx= 0.1, rely=0.5)
    login_enter_entry.place(relx= 0.3, rely=0.3)
    password_enter_entry.place(relx= 0.3, rely=0.5)
    reg_enter_button.place(relx= 0.43, rely=0.7)

def log_in_window():
    reg_button.place_forget()
    log_in_button.place_forget()

    title_lable.config(text="Вход")

    login_enter_label.place(relx=0.1, rely=0.3)
    password_enter_label.place(relx=0.1, rely=0.5)
    login_enter_entry.place(relx=0.3, rely=0.3)
    password_enter_entry.place(relx=0.3, rely=0.5)
    log_in_enter_button.place(relx=0.43, rely=0.7)

#/////////////////////////////////////////////////////////////////////////////////////





title_lable = Label(root, text="Enigma Chat", font=("Comic Sans MS", 20))
reg_button = Button(root, text="Регистрация", font=("Comic Sans MS", 20), command=reg_window)
log_in_button = Button(root, text="Вход", font=("Comic Sans MS", 20), command=log_in_window)

title_lable.place(relx= 0.38, rely = 0.1)
reg_button.place(relx= 0.35, rely = 0.3)
log_in_button.place(relx= 0.43, rely = 0.6)

root.mainloop()