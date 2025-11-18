from tkinter import *
from tkinter import messagebox

from client_api import ChatClient
from enigma import enigma_encrypt

client = ChatClient('localhost', 8080)

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
    result = client.login(login, password)

    if result['status'] == 'success':
        open_main_chat(result['user_id'])
    else:
        messagebox.showerror("Ошибка", result['message'])


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

    if not login or not password:
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return

    result = client.register(login, password)
    if result['status'] == 'success':
        messagebox.showinfo("Успех", "Регистрация завершена")
        show_page("login")
    else:
        messagebox.showerror("Ошибка", result['message'])


Button(register_page, text="Зарегистрироваться", font=("Comic Sans MS", 18),
       command=register_gui).pack(pady=15)

Button(register_page, text="Назад", command=lambda: show_page("welcome")).pack()

main_page = create_page("main")

# чаты (левая панель)
sidebar = Frame(main_page, width=250, bg="#f0f0f0")
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

Label(sidebar, text="Чаты", font=("Comic Sans MS", 16),
      bg="#ddd").pack(fill=X)

# Кнопка создания чата (справа сверху)
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

    result = client.get_user_chats(user_id)
    if result['status'] == 'success':
        chats = result['chats']
        for chat_id, other, encryption_enabled in chats:
            result_user = client.get_user_login(other)
            if result_user['status'] == 'success':
                username = result_user['login']
            else:
                username = "Неизвестный пользователь"

            # Добавляем иконку шифрования если оно включено
            chat_text = f"{username} {'🔒' if encryption_enabled else ''}"

            btn = Button(chat_list_frame, text=chat_text,
                         font=("Comic Sans MS", 14),
                         command=lambda c=chat_id, o=other: select_chat(c, o))
            btn.pack(fill=X, pady=2)

    chat_list_frame.update_idletasks()
    chat_list_canvas.configure(scrollregion=chat_list_canvas.bbox("all"))


def get_user_login(user_id):
    result = client.get_user_login(user_id)
    if result['status'] == 'success':
        return result['login']
    return "Неизвестный пользователь"


chat_area = Frame(main_page, bg="white")
chat_area.grid(row=0, column=1, sticky="nsew")

main_page.columnconfigure(1, weight=1)
main_page.rowconfigure(0, weight=1)

chat_area.rowconfigure(1, weight=1)
chat_area.columnconfigure(0, weight=1)

# шапка с кнопкой шифрования
chat_header = Frame(chat_area, bg="#ddd")
chat_header.grid(row=0, column=0, sticky="we")
chat_header.columnconfigure(0, weight=1)

chat_title = Label(chat_header, bg="#ddd", font=("Comic Sans MS", 16), anchor="w", padx=8)
chat_title.grid(row=0, column=0, sticky="we")

encryption_btn = Button(chat_header, text="Шифрование", font=("Comic Sans MS", 10),
                        command=lambda: open_encryption_dialog())
encryption_btn.grid(row=0, column=1, sticky="e", padx=8, pady=2)

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
        msg_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# биндим на canvas, не на весь root, чтобы прокрутка работала когда курсор над чатом
msg_canvas.bind_all("<MouseWheel>", _on_mousewheel)
msg_canvas.bind_all("<Button-4>", _on_mousewheel)
msg_canvas.bind_all("<Button-5>", _on_mousewheel)

# инпут
input_frame = Frame(chat_area, bg="white", pady=4)
input_frame.grid(row=2, column=0, sticky="we")
input_frame.columnconfigure(0, weight=1)

msg_entry = Entry(input_frame, font=("Comic Sans MS", 14))
msg_entry.grid(row=0, column=0, sticky="we", padx=(8, 5), pady=6)


# Привязка Enter к отправке сообщения
def on_enter_pressed(event):
    send_message()


msg_entry.bind('<Return>', on_enter_pressed)


def send_message():
    text = msg_entry.get()
    if text and hasattr(main_page, "current_chat"):
        result = client.send_message(text, main_page.current_chat, main_page.user_id)
        if result['status'] == 'success':
            msg_entry.delete(0, END)
            display_messages(main_page.current_chat)
        else:
            messagebox.showerror("Ошибка", result['message'])


send_button = Button(input_frame, text="Отправить", command=send_message)
send_button.grid(row=0, column=1, sticky="e", padx=(5, 8), pady=6)


def select_chat(chat_id, other_id):
    main_page.current_chat = chat_id
    chat_title.config(text=f"Чат с {get_user_login(other_id)}")
    display_messages(chat_id)


def display_messages(chat_id):
    for w in msg_frame.winfo_children():
        w.destroy()

    result = client.get_chat_messages(chat_id)
    if result['status'] == 'success':
        msgs = result['messages']

        # шифр чата
        enc_settings = client.get_chat_encryption_settings(chat_id)
        encryption_enabled = False
        if enc_settings['status'] == 'success':
            encryption_enabled = enc_settings['encryption_enabled']
            rotor_order = enc_settings['rotor_order']
            rotor_positions = enc_settings['rotor_positions']
            ring_settings = enc_settings['ring_settings']
            reflector = enc_settings['reflector']

        for msg in msgs:
            # Берем только первые 5 значений, игнорируем timestamp
            msg_id, text, code, chat, author = msg[:5]

            # Применяем шифрование если оно true
            display_text = text
            if encryption_enabled:
                display_text = enigma_encrypt(
                    text, rotor_order, rotor_positions, ring_settings, reflector
                )

            # моё
            if author == main_page.user_id:
                bubble = Label(
                    msg_frame,
                    text=display_text,
                    bg="#c8e6ff",  # голубой
                    font=("Comic Sans MS", 12),
                    padx=10,
                    pady=6,
                    wraplength=400,
                    justify=LEFT
                )
                bubble.pack(anchor="e", padx=10, pady=3)  # ПРАВО

            else:  # сабеседник
                bubble = Label(
                    msg_frame,
                    text=display_text,
                    bg="#e6e6e6",  # серый
                    font=("Comic Sans MS", 12),
                    padx=10,
                    pady=6,
                    wraplength=400,
                    justify=LEFT
                )
                bubble.pack(anchor="w", padx=10, pady=3)  # ЛЕВО

    msg_frame.update_idletasks()
    msg_canvas.yview_moveto(1.0)


def open_main_chat(user_id):
    main_page.user_id = user_id
    update_chat_list(user_id)
    show_page("main")


def open_create_chat_dialog(user_id):
    dialog = Toplevel(root)
    dialog.title("Создать чат")
    dialog.geometry("400x400")  # Увеличил высоту для кнопки
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    Label(dialog, text="Введите логин пользователя:",
          font=("Comic Sans MS", 12)).pack(pady=10)

    login_entry = Entry(dialog, font=("Comic Sans MS", 12))
    login_entry.pack(pady=5, padx=20, fill=X)

    # шифр
    encryption_frame = LabelFrame(dialog, text="Настройки шифрования", font=("Comic Sans MS", 10))
    encryption_frame.pack(pady=10, padx=20, fill=X)

    encryption_var = BooleanVar(value=True)
    encryption_check = Checkbutton(encryption_frame, text="Включить шифрование",
                                   variable=encryption_var, font=("Comic Sans MS", 10))
    encryption_check.pack(anchor="w", pady=5)

    # Поля для настроек Энигмы
    settings_frame = Frame(encryption_frame)
    settings_frame.pack(fill=X, padx=10, pady=5)

    Label(settings_frame, text="Порядок роторов (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    rotor_order_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    rotor_order_entry.insert(0, "1,2,3")
    rotor_order_entry.pack(fill=X, pady=2)

    Label(settings_frame, text="Позиции роторов (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    rotor_positions_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    rotor_positions_entry.insert(0, "А,А,А")
    rotor_positions_entry.pack(fill=X, pady=2)

    Label(settings_frame, text="Настройки колец (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    ring_settings_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    ring_settings_entry.insert(0, "0,0,0")
    ring_settings_entry.pack(fill=X, pady=2)

    Label(settings_frame, text="Рефлектор (A/B/C):", font=("Comic Sans MS", 9)).pack(anchor="w")
    reflector_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    reflector_entry.insert(0, "B")
    reflector_entry.pack(fill=X, pady=2)

    def create_chat_action():
        target_login = login_entry.get().strip()
        if not target_login:
            messagebox.showwarning("Ошибка", "Введите логин пользователя")
            return

        result = client.get_all_users()
        if result['status'] != 'success':
            messagebox.showerror("Ошибка", "Не удалось получить список пользователей")
            return

        all_users = result['users']
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

        result = client.chat_exists(user_id, target_user_id)
        if result['status'] == 'success' and result['exists']:
            messagebox.showinfo("Информация", f"Чат с пользователем '{target_login}' уже существует")
            dialog.destroy()
            return

        # Подготавливаем настройки шифрования
        encryption_settings = None
        if encryption_var.get():
            try:
                rotor_order = [int(x.strip()) for x in rotor_order_entry.get().split(',')]
                rotor_positions = [x.strip().upper() for x in rotor_positions_entry.get().split(',')]
                ring_settings = [int(x.strip()) for x in ring_settings_entry.get().split(',')]
                reflector = reflector_entry.get().strip().upper()

                encryption_settings = {
                    'rotor_order': rotor_order,
                    'rotor_positions': rotor_positions,
                    'ring_settings': ring_settings,
                    'reflector': reflector
                }
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неверные настройки шифрования: {e}")
                return

        result = client.create_chat(user_id, target_user_id, encryption_settings)
        if result['status'] == 'success':
            messagebox.showinfo("Успех", f"Чат с пользователем '{target_login}' создан")
            # Обновляем список чатов
            update_chat_list(user_id)
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", result['message'])

    button_frame = Frame(dialog)
    button_frame.pack(pady=10, fill=X, padx=20)

    Button(button_frame, text="Создать чат", font=("Comic Sans MS", 12),
           command=create_chat_action).pack(side=LEFT, padx=5)

    Button(button_frame, text="Отмена", font=("Comic Sans MS", 12),
           command=dialog.destroy).pack(side=RIGHT, padx=5)

    login_entry.focus_set()

    dialog.bind('<Return>', lambda e: create_chat_action())


def open_encryption_dialog():
    if not hasattr(main_page, "current_chat"):
        messagebox.showinfo("Информация", "Выберите чат для настройки шифрования")
        return

    password_dialog = Toplevel(root)
    password_dialog.title("Подтверждение пароля")
    password_dialog.geometry("300x150")
    password_dialog.resizable(False, False)
    password_dialog.transient(root)
    password_dialog.grab_set()

    Label(password_dialog, text="Введите ваш пароль:",
          font=("Comic Sans MS", 12)).pack(pady=15)

    password_entry = Entry(password_dialog, font=("Comic Sans MS", 12), show="*")
    password_entry.pack(pady=5, padx=20, fill=X)

    def verify_and_open_settings():
        password = password_entry.get()
        result = client.verify_password(main_page.user_id, password)
        if result['status'] == 'success':
            password_dialog.destroy()
            open_encryption_settings_dialog()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")
            password_entry.delete(0, END)

    Button(password_dialog, text="Подтвердить", font=("Comic Sans MS", 12),
           command=verify_and_open_settings).pack(pady=10)

    password_entry.focus_set()
    password_dialog.bind('<Return>', lambda e: verify_and_open_settings())


def open_encryption_settings_dialog():
    dialog = Toplevel(root)
    dialog.title("Управление шифрованием")
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    # Получаем текущие настройки
    result = client.get_chat_encryption_settings(main_page.current_chat)
    if result['status'] != 'success':
        messagebox.showerror("Ошибка", "Не удалось получить настройки шифрования")
        dialog.destroy()
        return

    current_settings = result

    Label(dialog, text="Настройки шифрования Энигмы",
          font=("Comic Sans MS", 14)).pack(pady=10)

    encryption_var = BooleanVar(value=current_settings['encryption_enabled'])
    encryption_check = Checkbutton(dialog, text="Включить шифрование",
                                   variable=encryption_var, font=("Comic Sans MS", 12))
    encryption_check.pack(anchor="w", pady=5, padx=20)

    # Поля для настроек Энигмы
    settings_frame = LabelFrame(dialog, text="Параметры Энигмы", font=("Comic Sans MS", 10))
    settings_frame.pack(pady=10, padx=20, fill=X)

    Label(settings_frame, text="Порядок роторов (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    rotor_order_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    rotor_order_entry.insert(0, ",".join(map(str, current_settings['rotor_order'])))
    rotor_order_entry.pack(fill=X, pady=2, padx=10)

    Label(settings_frame, text="Позиции роторов (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    rotor_positions_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    rotor_positions_entry.insert(0, ",".join(current_settings['rotor_positions']))
    rotor_positions_entry.pack(fill=X, pady=2, padx=10)

    Label(settings_frame, text="Настройки колец (через запятую):", font=("Comic Sans MS", 9)).pack(anchor="w")
    ring_settings_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    ring_settings_entry.insert(0, ",".join(map(str, current_settings['ring_settings'])))
    ring_settings_entry.pack(fill=X, pady=2, padx=10)

    Label(settings_frame, text="Рефлектор (A/B/C):", font=("Comic Sans MS", 9)).pack(anchor="w")
    reflector_entry = Entry(settings_frame, font=("Comic Sans MS", 9))
    reflector_entry.insert(0, current_settings['reflector'])
    reflector_entry.pack(fill=X, pady=2, padx=10)

    def save_settings():
        try:
            rotor_order = [int(x.strip()) for x in rotor_order_entry.get().split(',')]
            rotor_positions = [x.strip().upper() for x in rotor_positions_entry.get().split(',')]
            ring_settings = [int(x.strip()) for x in ring_settings_entry.get().split(',')]
            reflector = reflector_entry.get().strip().upper()

            settings = {
                'encryption_enabled': encryption_var.get(),
                'rotor_order': rotor_order,
                'rotor_positions': rotor_positions,
                'ring_settings': ring_settings,
                'reflector': reflector
            }

            result = client.update_chat_encryption_settings(main_page.current_chat, settings)
            if result['status'] == 'success':
                messagebox.showinfo("Успех", "Настройки шифрования обновлены")
                display_messages(main_page.current_chat)  # Обновляем отображение сообщений
                update_chat_list(main_page.user_id)  # Обновляем список чатов
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", result['message'])

        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверные настройки: {e}")

    def disable_encryption():
        encryption_var.set(False)
        save_settings()
    buttons_frame = Frame(dialog)
    buttons_frame.pack(pady=10)

    Button(buttons_frame, text="Сохранить настройки", font=("Comic Sans MS", 10),
           command=save_settings).pack(side=LEFT, padx=5)

    Button(buttons_frame, text="Отключить шифрование", font=("Comic Sans MS", 10),
           command=disable_encryption).pack(side=LEFT, padx=5)

    Button(buttons_frame, text="Выйти", font=("Comic Sans MS", 10),
           command=dialog.destroy).pack(side=LEFT, padx=5)

show_page("welcome")