# Імпорт бібліотек та модулів
import http.server
import socketserver
import socket
import threading
import json
import datetime
from urllib.parse import urlparse, parse_qs
from pymongo import MongoClient


# Створення базового HTTP-сервера
# Створення HTTP-сервера
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message':
            self.path = '/message.html'
        elif self.path == '/error':
            self.path = '/error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            username = data.get('username')[0]
            message = data.get('message')[0]

            # Відправка даних на Socket-сервер
            send_to_socket_server(username, message)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Message received!")
        else:
            self.send_error(404)
            self.end_headers()

# Функція відправки даних на Socket-сервер
def send_to_socket_server(username, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    message_data = {
        "username": username,
        "message": message,
        "date": str(datetime.datetime.now())
    }
    sock.sendall(json.dumps(message_data).encode('utf-8'))
    sock.close()

# Запуск HTTP-сервера
def start_http_server():
    PORT = 3000
    handler = SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving HTTP on port {PORT}")
    httpd.serve_forever()


# Створення Socket-сервера
# Створення Socket-сервера
def start_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 5000))
    sock.listen(5)
    print("Socket server is running on port 5000")

    client = MongoClient('mongodb://localhost:27017/')
    db = client['messages']
    collection = db['messages']

    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        if not data:
            break
        message_data = json.loads(data.decode('utf-8'))
        collection.insert_one(message_data)
        print(f"Message saved: {message_data}")
        conn.close()

# Запуск Socket-сервера в окремому потоці
socket_server_thread = threading.Thread(target=start_socket_server)
socket_server_thread.daemon = True
socket_server_thread.start()

# Запуск обох серверів
if __name__ == "__main__":
    http_server_thread = threading.Thread(target=start_http_server)
    http_server_thread.daemon = True
    http_server_thread.start()

    start_socket_server()
