import socket
import threading
import sqlite3
import json


class ChatServer:
    def __init__(self, host='0.0.0.0', port=1111):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    login TEXT, password TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages(
                    msg_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    text TEXT, code TEXT, chat INTEGER, author INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat(
                    chat_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    author INTEGER, address INTEGER
                )
            """)
            db.commit()

    def handle_client(self, client_socket, address):
        print(f"Новое подключение: {address}")

        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                response = self.process_request(request)
                client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"Ошибка с клиентом {address}: {e}")
        finally:
            client_socket.close()
            print(f"Клиент {address} отключен")

    def process_request(self, request):
        action = request.get('action')

        try:
            if action == 'login':
                return self.login(request['login'], request['password'])
            elif action == 'register':
                return self.register(request['login'], request['password'])
            elif action == 'get_user_chats':
                return self.get_user_chats(request['user_id'])
            elif action == 'get_chat_messages':
                return self.get_chat_messages(request['chat_id'])
            elif action == 'send_message':
                return self.send_message(
                    request['text'], request['chat_id'], request['author']
                )
            elif action == 'create_chat':
                return self.create_chat(
                    request['user1_id'], request['user2_id']
                )
            elif action == 'get_all_users':
                return self.get_all_users()
            elif action == 'chat_exists':
                return self.chat_exists(
                    request['user1_id'], request['user2_id']
                )
            else:
                return {'status': 'error', 'message': 'Неизвестное действие'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def login(self, login, password):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE login=?", (login,))
            data = cursor.fetchall()

            if not data:
                return {'status': 'error', 'message': 'Неверный логин'}
            if data[0][2] == password:
                return {'status': 'success', 'user_id': data[0][0]}
            else:
                return {'status': 'error', 'message': 'Неверный пароль'}

    def register(self, login, password):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)",
                           (login, password))
            db.commit()
            return {'status': 'success'}

    def get_user_chats(self, user_id):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT chat_id, 
                       CASE 
                           WHEN author = ? THEN address 
                           ELSE author 
                       END as other_user
                FROM chat 
                WHERE author = ? OR address = ?
            """, (user_id, user_id, user_id))
            chats = cursor.fetchall()
            return {'status': 'success', 'chats': chats}

    def get_chat_messages(self, chat_id):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages WHERE chat = ? ORDER BY msg_id ASC",
                           (chat_id,))
            messages = cursor.fetchall()
            return {'status': 'success', 'messages': messages}

    def send_message(self, text, chat_id, author):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO messages (text, code, chat, author) VALUES (?, ?, ?, ?)",
                (text, '', chat_id, author)
            )
            db.commit()
            return {'status': 'success'}

    def create_chat(self, user1_id, user2_id):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO chat (author, address) VALUES (?, ?)",
                (user1_id, user2_id)
            )
            db.commit()
            return {'status': 'success', 'chat_id': cursor.lastrowid}

    def get_all_users(self):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT user_id, login FROM users")
            users = cursor.fetchall()
            return {'status': 'success', 'users': users}

    def chat_exists(self, user1_id, user2_id):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT chat_id FROM chat 
                WHERE (author = ? AND address = ?) 
                   OR (author = ? AND address = ?)
            """, (user1_id, user2_id, user2_id, user1_id))
            exists = cursor.fetchone() is not None
            return {'status': 'success', 'exists': exists}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Сервер запущен на {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()


if __name__ == "__main__":
    server = ChatServer()
    server.start()