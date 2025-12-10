import socket
import threading
import json
import sqlite3
import argparse

from db import DatabaseClient


class ChatServer:
    def __init__(self, host='0.0.0.0', port=8080):  # Параметры конструктора
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.database = DatabaseClient()

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
        print(f"NEW REQUEST: {request}")
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
                    request['user1_id'], request['user2_id'],
                    request.get('encryption_settings')
                )
            elif action == 'get_all_users':
                return self.get_all_users()
            elif action == 'chat_exists':
                return self.chat_exists(
                    request['user1_id'], request['user2_id']
                )
            elif action == 'get_chat_encryption_settings':
                return self.get_chat_encryption_settings(request['chat_id'])
            elif action == 'update_chat_encryption_settings':
                return self.update_chat_encryption_settings(
                    request['chat_id'], request['settings']
                )
            elif action == 'verify_password':
                return self.verify_password(request['user_id'], request['password'])
            elif action == 'get_user_login':
                return self.get_user_login(request['user_id'])
            else:
                return {'status': 'error', 'message': 'Неизвестное действие'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_user_login(self, user_id):
        login = self.database.get_user_login(user_id)
        if login != "Неизвестный пользователь":
            return {'status': 'success', 'login': login}
        else:
            return {'status': 'error', 'message': 'Пользователь не найден'}

    def login(self, login, password):
        data = self.database.log_in(login)

        if not data:
            return {'status': 'error', 'message': 'Неверный логин'}
        if data[0][2] == password:
            return {'status': 'success', 'user_id': data[0][0]}
        else:
            return {'status': 'error', 'message': 'Неверный пароль'}

    def register(self, login, password):
        self.database.add_user(login, password)
        return {'status': 'success'}

    def get_user_chats(self, user_id):
        chats = self.database.get_user_chats(user_id)
        return {'status': 'success', 'chats': chats}

    def get_chat_messages(self, chat_id):
        messages = self.database.get_chat_messages(chat_id)
        return {'status': 'success', 'messages': messages}

    def send_message(self, text, chat_id, author):
        self.database.add_message(text, '', chat_id, author)
        return {'status': 'success'}

    def create_chat(self, user1_id, user2_id, encryption_settings=None):
        chat_id = self.database.create_chat(user1_id, user2_id)

        # Если есть настройки шифрования, обновляем их
        if encryption_settings:
            settings = {
                'encryption_enabled': True,
                'rotor_order': encryption_settings['rotor_order'],
                'rotor_positions': encryption_settings['rotor_positions'],
                'ring_settings': encryption_settings['ring_settings'],
                'reflector': encryption_settings['reflector']
            }
            self.update_chat_encryption_settings(chat_id, settings)

        return {'status': 'success', 'chat_id': chat_id}

    def get_all_users(self):
        users = self.database.get_all_users()
        return {'status': 'success', 'users': users}

    def chat_exists(self, user1_id, user2_id):
        exists = self.database.chat_exists(user1_id, user2_id)
        return {'status': 'success', 'exists': exists}

    def get_chat_encryption_settings(self, chat_id):
        with sqlite3.connect("enigma_db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT encryption_enabled, rotor_order, rotor_positions, ring_settings, reflector 
                FROM chat WHERE chat_id = ?
            """, (chat_id,))
            result = cursor.fetchone()

            if result:
                return {
                    'status': 'success',
                    'encryption_enabled': bool(result[0]),
                    'rotor_order': json.loads(result[1]),
                    'rotor_positions': json.loads(result[2]),
                    'ring_settings': json.loads(result[3]),
                    'reflector': result[4]
                }
            else:
                return {'status': 'error', 'message': 'Чат не найден'}

    def update_chat_encryption_settings(self, chat_id, settings):
        self.database.update_chat_encryption_settings(chat_id, settings)
        return {'status': 'success'}

    def verify_password(self, user_id, password):
        if self.database.verify_password(user_id, password):
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Неверный пароль'}

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
    parser = argparse.ArgumentParser(description='Запуск чат-сервера')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='IP адрес для прослушивания (по умолчанию: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Порт для прослушивания (по умолчанию: 8080)')

    args = parser.parse_args()

    print(f"Запуск сервера на {args.host}:{args.port}")
    server = ChatServer(host=args.host, port=args.port)
    server.start()