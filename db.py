import sqlite3
with sqlite3.connect("enigma_db.db") as db:
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT, password TEXT, chats TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages(msg_id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, code TEXT, chat INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat(chat_id INTEGER PRIMARY KEY AUTOINCREMENT, author INTEGER, address INTEGER)")

def add_user(login, password)  :
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f" INSERT INTO users (login, password) VALUES ('{login}','{password}')")
        db.commit()

def check_password(fetch, password):
    pass

def log_in(login, password):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE login='{login}'")
        data = cursor.fetchall()
        if not data:
            return "неверный логин"
        if data[0][2] == password:
            return data[0][0]
        else:
            return "неверный пароль"

