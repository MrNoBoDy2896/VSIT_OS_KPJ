import sys
from server import ChatServer
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Запуск чат-сервера Энигма')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='IP адрес для прослушивания (по умолчанию: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Порт для прослушивания (по умолчанию: 8080)')

    args = parser.parse_args()

    print(f"Запуск сервера Энигма на {args.host}:{args.port}")
    print("Для остановки сервера нажмите Ctrl+C")

    server = ChatServer(host=args.host, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        sys.exit(0)