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
    result = log_in(login, password)

    if isinstance(result, int):  # Если вернулся user_id (успешный вход)
        main_window(result)
    else:
        print(result)

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

#///////////////////////////////////Главное окно//////////////////////////////////////
def main_window(user_id):
    chat_frame.pack_forget()
    input_frame.pack_forget()

    title_lable.place_forget()
    reg_button.place_forget()
    log_in_button.place_forget()
    login_enter_label.place_forget()
    password_enter_label.place_forget()
    login_enter_entry.place_forget()
    password_enter_entry.place_forget()
    reg_enter_button.place_forget()
    log_in_enter_button.place_forget()


    main_container.pack(fill=BOTH, expand=True)

    sidebar_frame = Frame(main_container, width=200, bg='#f0f0f0')
    sidebar_frame.pack(side=LEFT, fill=Y)
    sidebar_frame.pack_propagate(False)

    sidebar_title = Label(sidebar_frame, text="Чаты", font=("Comic Sans MS", 16),
                          bg='#e0e0e0', pady=10)
    sidebar_title.pack(fill=X)

    chat_canvas = Canvas(sidebar_frame, bg='#f0f0f0', highlightthickness=0)
    scrollbar = Scrollbar(sidebar_frame, orient=VERTICAL, command=chat_canvas.yview)
    chat_scrollable_frame = Frame(chat_canvas, bg='#f0f0f0')

    chat_scrollable_frame.bind(
        "<Configure>",
        lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
    )

    chat_canvas.create_window((0, 0), window=chat_scrollable_frame, anchor="nw")
    chat_canvas.configure(yscrollcommand=scrollbar.set)

    chat_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # ЧАТ

    chat_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    chat_title = Label(chat_frame, text="Выберите чат", font=("Comic Sans MS", 16),
                       bg='#e0e0e0', pady=10)
    chat_title.pack(fill=X)

    messages_display_frame = Frame(chat_frame, bg='white')
    messages_display_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Н ечистим черновик
    input_frame.pack(fill=X, padx=10, pady=10)

    message_entry = Entry(input_frame, font=("Comic Sans MS", 14))
    message_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

    def send_message():
        text = message_entry.get()
        if text and hasattr(chat_frame, 'current_chat_id'):
            add_message(text, "", chat_frame.current_chat_id)
            display_messages(chat_frame.current_chat_id, messages_display_frame)
            message_entry.delete(0, END)

    send_button = Button(input_frame, text="Отправить", font=("Comic Sans MS", 12),
                         command=send_message)
    send_button.pack(side=RIGHT)

    new_chat_button = Button(sidebar_frame, text="+ Новый чат", font=("Comic Sans MS", 12),
                             bg='#4CAF50', fg='white', relief=FLAT, pady=10,
                             command=lambda: create_new_chat_window(user_id, chat_scrollable_frame, chat_title,
                                                                    messages_display_frame, chat_frame))
    new_chat_button.pack(fill=X, padx=5, pady=5)
    load_user_chats(user_id, chat_scrollable_frame, chat_title, messages_display_frame, chat_frame)


def load_user_chats(user_id, chat_scrollable_frame, chat_title, messages_frame, chat_frame):
    chats = get_user_chats(user_id)
    for chat in chats:
        chat_id, other_user_id = chat
        other_user_login = get_user_login(other_user_id)
        chat_btn = Button(chat_scrollable_frame, text=other_user_login, font=("Comic Sans MS", 12),
                          bg='#ffffff', relief=FLAT, pady=10, width=20,
                          command=lambda cid=chat_id, uid=other_user_id, user=other_user_login:
                          select_chat(cid, uid, user, chat_title, messages_frame, chat_frame))
        chat_btn.pack(fill=X, padx=5, pady=2)


def select_chat(chat_id, other_user_id, user_login, chat_title, messages_frame, chat_frame):
    chat_title.config(text=f"Чат с {user_login}")
    chat_frame.current_chat_id = chat_id
    chat_frame.current_other_user_id = other_user_id
    display_messages(chat_id, messages_frame)

    input_frame.pack_forget()
    input_frame.pack(fill=X, padx=10, pady=10)


def display_messages(chat_id, messages_display_frame):
    for widget in messages_display_frame.winfo_children():
        widget.destroy()

    messages = get_chat_messages(chat_id)

    msg_canvas = Canvas(messages_display_frame, bg='white', highlightthickness=0)
    msg_scrollbar = Scrollbar(messages_display_frame, orient=VERTICAL, command=msg_canvas.yview)
    msg_scrollable_frame = Frame(msg_canvas, bg='white')

    msg_scrollable_frame.bind(
        "<Configure>",
        lambda e: msg_canvas.configure(scrollregion=msg_canvas.bbox("all"))
    )

    msg_canvas.create_window((0, 0), window=msg_scrollable_frame, anchor="nw")
    msg_canvas.configure(yscrollcommand=msg_scrollbar.set)

    msg_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    msg_scrollbar.pack(side=RIGHT, fill=Y)

    for msg in messages:
        msg_id, text, code, chat = msg
        msg_label = Label(msg_scrollable_frame, text=text, font=("Comic Sans MS", 12),
                          bg='#e3f2fd', relief=RAISED, padx=10, pady=5, wraplength=400,
                          justify=LEFT)
        msg_label.pack(fill=X, padx=5, pady=2, anchor='w')
    msg_canvas.update_idletasks()
    msg_canvas.yview_moveto(1.0)


def create_new_chat_window(user_id, chat_scrollable_frame, chat_title, messages_frame, chat_frame):
    """Окно для создания нового чата"""
    new_chat_window = Toplevel(root)
    new_chat_window.title("Новый чат")
    new_chat_window.geometry("300x400")

    Label(new_chat_window, text="Выберите пользователя:", font=("Comic Sans MS", 14)).pack(pady=10)
    all_users = get_all_users()

    users_frame = Frame(new_chat_window)
    users_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    for user in all_users:
        user_id_other, user_login = user
        if user_id_other != user_id and not chat_exists(user_id, user_id_other):
            user_btn = Button(users_frame, text=user_login, font=("Comic Sans MS", 12),
                              command=lambda uid=user_id_other, login=user_login:
                              create_chat_and_close(user_id, uid, login, new_chat_window,
                                                    chat_scrollable_frame, chat_title, messages_frame, chat_frame))
            user_btn.pack(fill=X, pady=2)

    if not any(user[0] != user_id and not chat_exists(user_id, user[0]) for user in all_users):
        Label(users_frame, text="Нет пользователей для создания чата",
              font=("Comic Sans MS", 10), fg='gray').pack(pady=20)


def create_chat_and_close(user1_id, user2_id, user2_login, window, chat_scrollable_frame, chat_title, messages_frame,
                          chat_frame):
    """Создать чат и закрыть окно выбора"""
    chat_id = create_chat(user1_id, user2_id)
    window.destroy()

    chat_btn = Button(chat_scrollable_frame, text=user2_login, font=("Comic Sans MS", 12),
                      bg='#ffffff', relief=FLAT, pady=10, width=20,
                      command=lambda cid=chat_id, uid=user2_id, user=user2_login:
                      select_chat(cid, uid, user, chat_title, messages_frame, chat_frame))
    chat_btn.pack(fill=X, padx=5, pady=2)

    select_chat(chat_id, user2_id, user2_login, chat_title, messages_frame, chat_frame)

#/////////////////////////////////////////////////////////////////////////////////////
main_container = Frame(root)
chat_frame = Frame(main_container, bg='white')
input_frame = Frame(chat_frame, bg='white')

title_lable = Label(root, text="Enigma Chat", font=("Comic Sans MS", 20))
reg_button = Button(root, text="Регистрация", font=("Comic Sans MS", 20), command=reg_window)
log_in_button = Button(root, text="Вход", font=("Comic Sans MS", 20), command=log_in_window)

title_lable.place(relx= 0.38, rely = 0.1)
reg_button.place(relx= 0.35, rely = 0.3)
log_in_button.place(relx= 0.43, rely = 0.6)

root.mainloop()