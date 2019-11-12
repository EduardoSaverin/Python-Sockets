import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888

# SOCK_STREAM means that it is a TCP socket.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Notice We supply tuple here because we used AF_INET
server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]

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


while True:
    read_sockets, _, socket_with_exceptions = select.select(socket_list, [], socket_list)
    for current_socket in read_sockets:
        if current_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            socket_list.append(client_socket)
            clients[client_socket] = user
            print(
                f'Accepted new connection from {client_address[0]} : {client_address[1]}')
        else:
            message = receive_message(current_socket)
            if message is False:
                print(
                    f"Connection closed from {clients[current_socket]['data'].decode('utf-8')}")
                socket_list.remove(current_socket)
                del clients[current_socket]
                continue
            user = clients[current_socket]
            print(f"Received messsage from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            for client_socket in clients:
                if client_socket != current_socket:
                    client_socket.send(user['header']+user['data']+message['header']+message['data'])
    for current_socket in socket_with_exceptions:
        socket_list.remove(current_socket)
        del clients[current_socket]
