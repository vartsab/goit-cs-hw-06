import http.server
import socket
import socketserver
import json
import datetime
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import threading

# MongoDB client setup
client = MongoClient('mongodb://mongodb:27017/')
db = client['messages']
collection = db['messages']

# HTTP Server for Web Application
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

            # Send data to the socket server
            send_to_socket_server(username, message)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Message received!")
        else:
            self.send_error(404)
            self.end_headers()

def send_to_socket_server(username, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))  # Use 'localhost' or '127.0.0.1' for local testing
    message_data = {
        "username": username,
        "message": message,
        "date": str(datetime.datetime.now())
    }
    sock.sendall(json.dumps(message_data).encode('utf-8'))
    sock.close()

def start_http_server():
    PORT = 3000
    handler = SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving HTTP on port {PORT}")
    httpd.serve_forever()

# Socket Server for handling messages
def start_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 5000))
    sock.listen(5)
    print("Socket server is running on port 5000")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        if not data:
            break
        message_data = json.loads(data.decode('utf-8'))
        collection.insert_one(message_data)
        print(f"Message saved: {message_data}")
        conn.close()

# Run both servers in separate threads
if __name__ == "__main__":
    threading.Thread(target=start_http_server).start()
    threading.Thread(target=start_socket_server).start()

