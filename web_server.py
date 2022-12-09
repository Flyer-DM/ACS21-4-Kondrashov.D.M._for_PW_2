import socket
import os
import random
from datetime import datetime


SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
OPTIONS = (80, os.getcwd(), 8192, ['html', 'jpg', 'png', 'gif'])
HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
HDRS404 = 'HTTP/1.1 404 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
HDRS403 = 'HTTP/1.1 403 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
try:
    with open('options.txt', 'r') as f:
        settings = f.read().split('\n')
    port, dirname, max_size, type_list = int(settings[0]), settings[1], int(settings[2]), settings[3].split()
except FileNotFoundError:
    with open('options.txt', 'w') as f:
        f.write('\n'.join(map(str, OPTIONS[:3])) + '\n' + ' '.join(OPTIONS[3]))
        port, dirname, max_size, type_list = OPTIONS


def logger(message: str) -> None:
    """Сохранение лог файла сервера"""
    with open('server_logs.txt', 'a') as logs:
        logs.write(f"{datetime.now()} | {message}\n")
    print(message)


def reciever(client_sock: socket.socket) -> str:
    """Получение сообщения от клиента сервера"""
    return client_sock.recv(max_size).decode()


def loader(request: str):
    """Обработчик GET запроса от клиента"""
    path = request.split('\n')[0]
    if len(path) > 0:
        path = path[4:path.rindex(' ')]
        try:
            if '.' in path and path.split('.')[1] in type_list:
                with open(dirname + path, 'rb') as f:
                    return HDRS.encode() + f.read()
            else:
                with open(dirname + '\\403_error.html', 'rb') as f:
                    return HDRS403.encode() + f.read()
        except FileNotFoundError:
            with open(dirname + '\\404_error.html', 'rb') as f:
                response = f.read()
            return HDRS404.encode() + response


def client_handling(sock: socket.socket) -> None:
    """Подключение и получение запросов от клиента"""
    while True:
        client_socket, address = sock.accept()
        data = reciever(client_socket)
        answer = loader(data)
        request = data.split('\n')[0].replace('\r', '')
        if answer is not None:
            client_socket.send(answer)
            logger(f"Клиент {address[0]} | Запрос {request}")
            client_socket.shutdown(socket.SHUT_WR)


def server_serving(sock: socket.socket, port: int) -> None:
    """Запуск сервера"""
    logger("Включение сервера.")
    try:
        while True:
            try:
                sock.bind(('127.0.0.1', port))
                logger(f"Используется порт: {port}")
                break
            except OSError:
                logger(f"Порт {port} занят. Переключение...")
                port = random.randint(8080, 8800)
        sock.listen(10)
        client_handling(sock)
    except KeyboardInterrupt:
        sock.close()


if __name__ == '__main__':
    server_serving(SOCK, port)
