import time
import threading
from gui import *
from server import *


def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()


def run_server():
    import socket as s

    server = s.socket(s.AF_INET, s.SOCK_STREAM)
    server.bind(("localhost", 1111))
    server.listen()
    print("Сервер запущен на localhost:1111")

    while True:
        try:
            client, address = server.accept()
            print(f"Подключен клиент: {address}")

            # Обработка клиента в отдельном потоке
            client_thread = threading.Thread(target=handle_client, args=(client,))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            print(f"Ошибка сервера: {e}")
            break


def handle_client(client):
    flag = True
    while flag:
        try:
            msg = client.recv(1024).decode("utf-8")
            if msg == "q":
                flag = False
            else:
                print(f"Сообщение от клиента: {msg}")
            client.send(input("Сервер: ").encode("utf-8"))
        except:
            break

    client.close()


if __name__ == "__main__":
    start_server()
    time.sleep(1)
    root.mainloop()