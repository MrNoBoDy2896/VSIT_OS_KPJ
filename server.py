import socket as s

server = s.socket(s.AF_INET, s.SOCK_STREAM)
server.bind(("localhost", 1111))

server.listen()

client, address = server.accept()

flag = True
while flag:
    msg = client.recv(1024).decode("utf-8")
    if msg == "q":
        flag = False
    else:
        print(msg)
    client.send(input("Сервер: ").encode("utf-8"))


client.close()