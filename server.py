import socket as s

def run_server():
    server = s.socket(s.AF_INET, s.SOCK_STREAM)
    server.bind(("localhost", 1111))
    server.listen()
    print("Сервер запущен на localhost:1111")

    client, address = server.accept()
    print(f"Подключен клиент: {address}")

    flag = True
    while flag:
        msg = client.recv(1024).decode("utf-8")
        if msg == "q":
            flag = False
        else:
            print(msg)
        client.send(input("Сервер: ").encode("utf-8"))

    client.close()

if __name__ == "__main__":
    run_server()