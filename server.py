import socket
import select
from typing import List, Dict

HEADER_LENGTH: int = 10
IP: str = "127.0.0.1"
PORT: int = 9876


class ChatServer(object):
    def __init__(self):
        # SOCK_STREAM means that it is a TCP socket.
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Notice We supply tuple here because we used AF_INET
        server_socket.bind((IP, PORT))
        server_socket.listen(10)
        self.server_socket: socket.socket = server_socket
        print(f'Server started on {IP}:{PORT}')
        self.SOCKET_LIST: List[socket.socket] = [server_socket]
        self.clients: Dict[socket.socket, str] = {}
        self.start_server()

    def receive_message(self, client_socket: socket.socket):
        try:
            # Get header to know length of buffer size
            message_length = client_socket.recv(HEADER_LENGTH).decode("utf-8")
            print(f"Message Length {message_length}")
            return {'header': len(message_length), 'data': message_length.strip()}
        except:
            pass

    def broadcast(self, message: str, current_socket: socket.socket = None):
        for client in self.clients.keys():
            if client != self.server_socket and client != current_socket:
                client.send(('\n' + message).encode("utf-8"))

    def start_server(self):
        while True:
            read_sockets, write_sockets, socket_with_exceptions = select.select(self.SOCKET_LIST, [], [])
            for current_socket in read_sockets:
                # When a recv() returns 0 bytes, it means the other side has closed (or is in the process of closing)
                # the connection. You will not receive any more data on this connection ever. Though you may be able
                # to send data successfully.
                if current_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    data = self.receive_message(client_socket)
                    print(f"Data {data}")
                    user = data['data']
                    print(user)
                    if not user:
                        continue
                    self.SOCKET_LIST.append(client_socket)
                    self.clients[client_socket] = user
                    print(f'Accepted new connection from {client_address[0]} : {client_address[1]}')
                    self.broadcast(f"#{user} has joined")
                else:
                    try:
                        message = self.receive_message(current_socket)
                        if not message['data']:
                            print(
                                f"Connection closed from {self.clients[current_socket]}")
                            self.broadcast(f"#{self.clients[current_socket]} has left")
                            self.SOCKET_LIST.remove(current_socket)
                            del self.clients[current_socket]
                            continue
                        user = self.clients[current_socket]
                        print(f"Received message from {user}: {message['data']}")
                        if message['data']:
                            self.broadcast(f"#{user} >> {message['data']}", current_socket)
                    except:
                        self.broadcast(f"#{self.clients[current_socket]} has left")
            for current_socket in socket_with_exceptions:
                self.SOCKET_LIST.remove(current_socket)
                del self.clients[current_socket]


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_server()
