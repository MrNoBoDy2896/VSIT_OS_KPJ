from tkinter import *
from tkinter import messagebox
from db import *

root = Tk()
root.title("Enigma Chat")
root.geometry("600x400")

container = Frame(root)
container.pack(fill="both", expand=True)


container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=1)

pages = {}

def create_page(name):
    frame = Frame(container)
    frame.grid(row=0, column=0, sticky="nsew")
    pages[name] = frame
    return frame


def open_create_chat_dialog(user_id):
    dialog = Toplevel(root)
    dialog.title("Создать чат")
    dialog.geometry("300x150")
    dialog.resizable(False, False)

    Label(dialog, text="Введите логин пользователя:",
          font=("Comic Sans MS", 12)).pack(pady=10)

    login_entry = Entry(dialog, font=("Comic Sans MS", 12))
    login_entry.pack(pady=5, padx=20, fill=X)

    def create_chat_action():
        target_login = login_entry.get().strip()
        if not target_login:
            messagebox.showwarning("Ошибка", "Введите логин пользователя")
            return

        all_users = get_all_users()
        target_user = None

        for user in all_users:
            if user[1] == target_login:
                target_user = user
                break

        if not target_user:
            messagebox.showwarning("Ошибка", f"Пользователь '{target_login}' не найден")
            return

        target_user_id = target_user[0]

        if target_user_id == user_id:
            messagebox.showwarning("Ошибка", "Нельзя создать чат с самим собой")
            return

        if chat_exists(user_id, target_user_id):
            messagebox.showinfo("Информация", f"Чат с пользователем '{target_login}' уже существует")
            dialog.destroy()
            return

        create_chat(user_id, target_user_id)
        messagebox.showinfo("Успех", f"Чат с пользователем '{target_login}' создан")

        update_chat_list(user_id)
        dialog.destroy()

    Button(dialog, text="Создать чат", font=("Comic Sans MS", 12),
           command=create_chat_action).pack(pady=10)

    login_entry.focus_set()
    dialog.bind('<Return>', lambda e: create_chat_action())

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

#чаты (левая панель)
sidebar = Frame(main_page, width=250, bg="#f0f0f0")
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

Label(sidebar, text="Чаты", font=("Comic Sans MS", 16),
      bg="#ddd").pack(fill=X)
create_chat_btn = Button(sidebar, text="Создать чат", font=("Comic Sans MS", 12),
                        command=lambda: open_create_chat_dialog(main_page.user_id))
create_chat_btn.pack(pady=5)

chat_list_canvas = Canvas(sidebar, bg="#f0f0f0", highlightthickness=0)
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
chat_area.grid(row=0, column=1, sticky="nsew")

main_page.columnconfigure(1, weight=1)
main_page.rowconfigure(0, weight=1)

chat_area.rowconfigure(1, weight=1)
chat_area.columnconfigure(0, weight=1)

# шапка
chat_title = Label(chat_area, bg="#ddd", font=("Comic Sans MS", 16), anchor="w", padx=8)
chat_title.grid(row=0, column=0, sticky="we")

# сам чат
messages_display = Frame(chat_area, bg="white")
messages_display.grid(row=1, column=0, sticky="nsew")
messages_display.rowconfigure(0, weight=1)
messages_display.columnconfigure(0, weight=1)

msg_canvas = Canvas(messages_display, bg="white", highlightthickness=0)
msg_canvas.grid(row=0, column=0, sticky="nsew")

msg_scrollbar = Scrollbar(messages_display, orient="vertical", command=msg_canvas.yview)
msg_scrollbar.grid(row=0, column=1, sticky="ns")

msg_canvas.configure(yscrollcommand=msg_scrollbar.set)

msg_frame = Frame(msg_canvas, bg="white")
canvas_window = msg_canvas.create_window((0, 0), window=msg_frame, anchor="nw")

def _on_canvas_config(event):
    msg_canvas.itemconfig(canvas_window, width=event.width)
msg_canvas.bind("<Configure>", _on_canvas_config)

msg_frame.bind("<Configure>", lambda e: msg_canvas.configure(scrollregion=msg_canvas.bbox("all")))

def _on_mousewheel(event):
    if event.num == 4:
        msg_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        msg_canvas.yview_scroll(1, "units")
    else:
        msg_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# биндим на canvas, не на весь root, чтобы прокрутка работала когда курсор над чатом
msg_canvas.bind_all("<MouseWheel>", _on_mousewheel)
msg_canvas.bind_all("<Button-4>", _on_mousewheel)
msg_canvas.bind_all("<Button-5>", _on_mousewheel)


# инпут
input_frame = Frame(chat_area, bg="white", pady=4)
input_frame.grid(row=2, column=0, sticky="we")
input_frame.columnconfigure(0, weight=1)

msg_entry = Entry(input_frame, font=("Comic Sans MS", 14))
msg_entry.grid(row=0, column=0, sticky="we", padx=(8,5), pady=6)

def send_message():
    text = msg_entry.get()
    if text and hasattr(main_page, "current_chat"):
        add_message(text, "", main_page.current_chat, main_page.user_id)
        msg_entry.delete(0, END)
        display_messages(main_page.current_chat)

def on_enter_pressed(event):
    send_message()

msg_entry.bind('<Return>', on_enter_pressed)
send_button = Button(input_frame, text="Отправить", command=send_message)
send_button.grid(row=0, column=1, sticky="e", padx=(5,8), pady=6)


def select_chat(chat_id, other_id):
    main_page.current_chat = chat_id
    chat_title.config(text=f"Чат с {get_user_login(other_id)}")
    display_messages(chat_id)

def display_messages(chat_id):
    for w in msg_frame.winfo_children():
        w.destroy()

    msgs = get_chat_messages(chat_id)

    for msg in msgs:
        msg_id, text, code, chat, author = msg

        # моё
        if author == main_page.user_id:
            bubble = Label(
                msg_frame,
                text=text,
                bg="#c8e6ff",      # голубой
                font=("Comic Sans MS", 12),
                padx=10,
                pady=6,
                wraplength=400,
                justify=LEFT
            )
            bubble.pack(anchor="e", padx=10, pady=3)   #  ПРАВО

        else:# сабеседник
            bubble = Label(
                msg_frame,
                text=text,
                bg="#e6e6e6",      # серый
                font=("Comic Sans MS", 12),
                padx=10,
                pady=6,
                wraplength=400,
                justify=LEFT
            )
            bubble.pack(anchor="w", padx=10, pady=3)   # ЛЕВО

    msg_frame.update_idletasks()
    msg_canvas.yview_moveto(1.0)

def open_main_chat(user_id):
    main_page.user_id = user_id
    update_chat_list(user_id)
    show_page("main")

show_page("welcome")
root.mainloop()
