import socket
import errno
import sys
import threading

HEADER_LENGTH = 4096
IP = "127.0.0.1"
PORT = 9876


class ChatClient(object):
    def __init__(self):
        username = input('Enter Username: ')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        client_socket.settimeout(1000)
        client_socket.setblocking(False)
        self.client_socket = client_socket
        self.username: str = username
        # :< here is formatting basically, we are trying to keep number left aligned here
        # username_header = f"{len(username):<{HEADER_LENGTH}}"
        # print(username_header)
        client_socket.send(self.username.encode("utf-8"))
        threading.Thread(target=self.message_receiver).start()
        threading.Thread(target=self.message_sender).start()

    def message_sender(self):
        while True:
            message = input(f"#{str(self.username)} >>")
            if message:
                message = message.encode('utf-8')
                self.client_socket.send(message)

    def message_receiver(self):
        while True:
            try:
                # Receive Message
                # First get bytes of username
                data = self.client_socket.recv(HEADER_LENGTH).decode("utf-8")
                if not data:
                    print("Connection closed by server")
                    sys.exit()
                print(data)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('[Error] While Reading', str(e))
                    sys.exit()
                continue
            except Exception as e:
                print('[Error]', str(e))
                sys.exit()


if __name__ == '__main__':
    client = ChatClient()
