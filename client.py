import socket
import select
import errno
import sys
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888

username = input('Enter Username: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = username.encode('utf-8')
# :< here is formatting basically, we are trying to keep number left aligned here
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header+username)

def message_sender():
    while True:
        message = input(f"{str(username)} >")
        if message:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header+message)

def message_receiver():
    while True:
        try:
            while True:
                # Recieve Message
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by server")
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8'))
                message = client_socket.recv(message_length).decode('utf-8')
                print(f"{username} > {message}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('[Error] While Reading',str(e))
                sys.exit()
            continue
        except Exception as e:
            print('[Error]',str(e))
            sys.exit()

threading.Thread(target=message_receiver).start()
threading.Thread(target=message_sender).start()