import socket
import json


class ChatClient:
    def __init__(self, host='localhost', port=1111):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def send_request(self, request):
        try:
            if not self.socket:
                if not self.connect():
                    return {'status': 'error', 'message': 'Не удалось подключиться'}

            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def login(self, login, password):
        return self.send_request({
            'action': 'login',
            'login': login,
            'password': password
        })

    def register(self, login, password):
        return self.send_request({
            'action': 'register',
            'login': login,
            'password': password
        })

    def get_user_chats(self, user_id):
        return self.send_request({
            'action': 'get_user_chats',
            'user_id': user_id
        })

    def get_chat_messages(self, chat_id):
        return self.send_request({
            'action': 'get_chat_messages',
            'chat_id': chat_id
        })

    def send_message(self, text, chat_id, author):
        return self.send_request({
            'action': 'send_message',
            'text': text,
            'chat_id': chat_id,
            'author': author
        })

    def create_chat(self, user1_id, user2_id):
        return self.send_request({
            'action': 'create_chat',
            'user1_id': user1_id,
            'user2_id': user2_id
        })

    def get_all_users(self):
        return self.send_request({
            'action': 'get_all_users'
        })

    def chat_exists(self, user1_id, user2_id):
        return self.send_request({
            'action': 'chat_exists',
            'user1_id': user1_id,
            'user2_id': user2_id
        })

    def close(self):
        if self.socket:
            self.socket.close()