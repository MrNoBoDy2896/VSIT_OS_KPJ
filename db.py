import sqlite3


class DatabaseClient:

    def __init__(self):
        self.connection = sqlite3.connect("enigma_db.db", check_same_thread=False)

    def add_user(self, login, password):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f" INSERT INTO users (login, password) VALUES ('{login}','{password}')")
            db.commit()

    def check_password(self, fetch, password):
        pass

    def log_in(self, login):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM users WHERE login='{login}'")
            data = cursor.fetchall()
        return data

    def get_user_chats(self, user_id):
        with self.connection as db:
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

    def get_user_login(self, user_id):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT login FROM users WHERE user_id = {user_id}")
            result = cursor.fetchone()
            return result[0] if result else "Неизвестный пользователь"

    def get_chat_messages(self, chat_id):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM messages WHERE chat = {chat_id} ORDER BY msg_id ASC")
            return cursor.fetchall()

    def add_message(self, text, code, chat_id, author):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO messages (text, code, chat, author) VALUES ('{text}', '{code}', {chat_id}, {author})")
            db.commit()

    def create_chat(self, user1_id, user2_id):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f"INSERT INTO chat (author, address) VALUES ({user1_id}, {user2_id})")
            db.commit()
            return cursor.lastrowid

    def get_all_users(self):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute("SELECT user_id, login FROM users")
            return cursor.fetchall()

    def chat_exists(self, user1_id, user2_id):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute(f"""
                SELECT chat_id FROM chat 
                WHERE (author = {user1_id} AND address = {user2_id}) 
                   OR (author = {user2_id} AND address = {user1_id})
            """)
            return cursor.fetchone() is not None
