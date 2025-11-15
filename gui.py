from tkinter import *
from db import *

root = Tk()
root.title("Enigma Chat")
root.geometry("590x400")

container = Frame(root)
container.pack(fill="both", expand=True)

pages = {}

def create_page(name):
    frame = Frame(container)
    frame.grid(row=0, column=0, sticky="nsew")
    pages[name] = frame
    return frame

def show_page(name):
    pages[name].tkraise()

welcome_page = create_page("welcome")

Label(welcome_page, text="Enigma Chat", font=("Comic Sans MS", 24)).pack(pady=40)

Button(welcome_page, text="Вход", font=("Comic Sans MS", 18),
       command=lambda: show_page("login")).pack(pady=10)

Button(welcome_page, text="Регистрация", font=("Comic Sans MS", 18),
       command=lambda: show_page("register")).pack(pady=10)


login_page = create_page("login")

Label(login_page, text="Вход", font=("Comic Sans MS", 22)).pack(pady=20)

login_entry_l = Entry(login_page, font=("Comic Sans MS", 16))
login_entry_l.pack(pady=5)
login_entry_l.insert(0, "")

password_entry_l = Entry(login_page, font=("Comic Sans MS", 16), show="*")
password_entry_l.pack(pady=5)
password_entry_l.insert(0, "")

def log_in_gui():
    login = login_entry_l.get()
    password = password_entry_l.get()
    result = log_in(login, password)

    if isinstance(result, int):
        open_main_chat(result)
    else:
        print(result)

Button(login_page, text="Войти", font=("Comic Sans MS", 18),
       command=log_in_gui).pack(pady=15)

Button(login_page, text="Назад", command=lambda: show_page("welcome")).pack()


register_page = create_page("register")

Label(register_page, text="Регистрация", font=("Comic Sans MS", 22)).pack(pady=20)

login_entry_r = Entry(register_page, font=("Comic Sans MS", 16))
login_entry_r.pack(pady=5)
login_entry_r.insert(0, "")

password_entry_r = Entry(register_page, font=("Comic Sans MS", 16), show="*")
password_entry_r.pack(pady=5)
password_entry_r.insert(0, "")

def register_gui():
    login = login_entry_r.get()
    password = password_entry_r.get()

    add_user(login, password)
    show_page("login")

Button(register_page, text="Зарегистрироваться", font=("Comic Sans MS", 18),
       command=register_gui).pack(pady=15)

Button(register_page, text="Назад", command=lambda: show_page("welcome")).pack()


main_page = create_page("main")

# Левая панель — список чатов
sidebar = Frame(main_page, width=250, bg="#f0f0f0")
sidebar.pack(side=LEFT, fill=Y)
sidebar.pack_propagate(False)

Label(sidebar, text="Чаты", font=("Comic Sans MS", 16),
      bg="#ddd").pack(fill=X)

chat_list_canvas = Canvas(sidebar, bg="#f0f0f0")
chat_list_canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar = Scrollbar(sidebar, command=chat_list_canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
chat_list_canvas.configure(yscrollcommand=scrollbar.set)

chat_list_frame = Frame(chat_list_canvas, bg="#f0f0f0")
chat_list_canvas.create_window((0, 0), window=chat_list_frame, anchor="nw")

def update_chat_list(user_id):
    for widget in chat_list_frame.winfo_children():
        widget.destroy()

    chats = get_user_chats(user_id)
    for chat_id, other in chats:
        btn = Button(chat_list_frame, text=get_user_login(other),
                     font=("Comic Sans MS", 14),
                     command=lambda c=chat_id, o=other: select_chat(c, o))
        btn.pack(fill=X, pady=2)

    chat_list_frame.update_idletasks()
    chat_list_canvas.configure(scrollregion=chat_list_canvas.bbox("all"))

chat_area = Frame(main_page, bg="white")
chat_area.pack(side=RIGHT, fill=BOTH, expand=True)

chat_title = Label(chat_area, text="Выберите чат", font=("Comic Sans MS", 18),
                   bg="#ddd")
chat_title.pack(fill=X)

messages_display = Frame(chat_area, bg="white")
messages_display.pack(fill=BOTH, expand=True)

input_frame = Frame(chat_area, bg="white")
input_frame.pack(fill=X)

msg_entry = Entry(input_frame, font=("Comic Sans MS", 14))
msg_entry.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)

def send_message():
    text = msg_entry.get()
    if text and hasattr(main_page, "current_chat"):
        add_message(text, "", main_page.current_chat)
        msg_entry.delete(0, END)
        display_messages(main_page.current_chat)

Button(input_frame, text="Отправить", command=send_message).pack(side=RIGHT, padx=5)


def select_chat(chat_id, other_id):
    main_page.current_chat = chat_id
    chat_title.config(text=f"Чат с {get_user_login(other_id)}")
    display_messages(chat_id)


def display_messages(chat_id):
    for w in messages_display.winfo_children():
        w.destroy()

    msgs = get_chat_messages(chat_id)

    canvas = Canvas(messages_display)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    msg_scroll = Scrollbar(messages_display, command=canvas.yview)
    msg_scroll.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=msg_scroll.set)

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    for msg in msgs:
        Label(frame, text=msg[1], bg="#e3f2fd",
              anchor="w", justify=LEFT,
              font=("Comic Sans MS", 12), wraplength=350).pack(fill=X, pady=2, padx=5)

    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def open_main_chat(user_id):
    main_page.user_id = user_id
    update_chat_list(user_id)
    show_page("main")

show_page("welcome")
root.mainloop()
