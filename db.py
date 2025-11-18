import sqlite3
import json


class DatabaseClient:

    def __init__(self):
        self.connection = sqlite3.connect("enigma_db.db", check_same_thread=False)

    def get_chat_encryption_settings(self, chat_id):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT encryption_enabled, rotor_order, rotor_positions, ring_settings, reflector 
                FROM chat WHERE chat_id = ?
            """, (chat_id,))
            result = cursor.fetchone()

            if result:
                return {
                    'encryption_enabled': bool(result[0]),
                    'rotor_order': json.loads(result[1]),
                    'rotor_positions': json.loads(result[2]),
                    'ring_settings': json.loads(result[3]),
                    'reflector': result[4]
                }
            return None

    def update_chat_encryption_settings(self, chat_id, settings):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE chat SET 
                encryption_enabled = ?,
                rotor_order = ?,
                rotor_positions = ?,
                ring_settings = ?,
                reflector = ?
                WHERE chat_id = ?
            """, (
                settings['encryption_enabled'],
                json.dumps(settings['rotor_order']),
                json.dumps(settings['rotor_positions']),
                json.dumps(settings['ring_settings']),
                settings['reflector'],
                chat_id
            ))
            db.commit()

    def verify_password(self, user_id, password):
        with self.connection as db:
            cursor = db.cursor()
            cursor.execute("SELECT password FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result and result[0] == password

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
            cursor.execute("""
                SELECT chat_id, 
                       CASE 
                           WHEN author = ? THEN address 
                           ELSE author 
                       END as other_user,
                       encryption_enabled
                FROM chat 
                WHERE author = ? OR address = ?
            """, (user_id, user_id, user_id))
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
            cursor.execute("""
                SELECT chat_id FROM chat 
                WHERE (author = ? AND address = ?) 
                   OR (author = ? AND address = ?)
            """, (user1_id, user2_id, user2_id, user1_id))
            return cursor.fetchone() is not None
