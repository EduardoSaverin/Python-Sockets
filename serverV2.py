import socket
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"

connected_sockets = []
clients = {}

def receive_message(client_socket):
    try:
        # Get header to know length of buffer size
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        msg_length = int(message_header.decode('utf-8').strip())
        # Use that length to read full message at once
        return {'header': message_header, 'data': client_socket.recv(msg_length)}
    except:
        pass

class ThreadServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host,self.port))

    def listen(self,queue_size):
        self.socket.listen(queue_size)
        while True:
            client, address = self.socket.accept()
            connected_sockets.append(client)
            user = receive_message(client)
            if user is False:
                continue
            clients[client] = user
            print(f'Accepted new connection from {address[0]} : {address[1]}')
            client.settimeout(60*5)
            threading.Thread(target=self.listen_to_client,args=(client,address)).start()

    def listen_to_client(self, client, address):
        while True:
            try:
                message = receive_message(client)
                if message:
                    if message is False:
                        print(f"Connection closed from {clients[client]['data'].decode('utf-8')}")
                        continue
                    user = clients[client]
                    print(f"Received messsage from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                    for other_clients in connected_sockets:
                        if client != other_clients:
                            other_clients.send(user['header']+user['data']+message['header']+message['data'])
                else:
                    raise Exception('Client Disconnected')
            except:
                del clients[client]
                connected_sockets.remove(client)
            
            
if __name__ == '__main__':
    while True:
        port = input("Port: ")
        try:
            port = int(port)
            break
        except ValueError:
            pass
    ThreadServer(IP,port).listen(5)