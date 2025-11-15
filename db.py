import sqlite3
with sqlite3.connect("enigma_db.db") as db:
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT, password TEXT, chats TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages(msg_id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, code TEXT, chat INTEGER, author INTEGER)")
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

def get_user_chats(user_id):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"""
            SELECT chat_id, 
                   CASE 
                       WHEN author = {user_id} THEN address 
                       ELSE author 
                   END as other_user
            FROM chat 
            WHERE author = {user_id} OR address = {user_id}
        """)
        return cursor.fetchall()

def get_user_login(user_id):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT login FROM users WHERE user_id = {user_id}")
        result = cursor.fetchone()
        return result[0] if result else "Неизвестный пользователь"

def get_chat_messages(chat_id):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM messages WHERE chat = {chat_id} ORDER BY msg_id ASC")
        return cursor.fetchall()

def add_message(text, code, chat_id, author):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO messages (text, code, chat, author) VALUES ('{text}', '{code}', {chat_id}, {author})")
        db.commit()

def create_chat(user1_id, user2_id):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO chat (author, address) VALUES ({user1_id}, {user2_id})")
        db.commit()
        return cursor.lastrowid

def get_all_users():
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT user_id, login FROM users")
        return cursor.fetchall()

def chat_exists(user1_id, user2_id):
    with sqlite3.connect("enigma_db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"""
            SELECT chat_id FROM chat 
            WHERE (author = {user1_id} AND address = {user2_id}) 
               OR (author = {user2_id} AND address = {user1_id})
        """)
        return cursor.fetchone() is not None