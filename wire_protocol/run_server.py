import server
import socket
import threading

HOST = '127.0.0.1'
PORT = 6000

if __name__ == '__main__':
    socket_loc_map = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(0)
    server_socket.bind((HOST, PORT))
    print("Server started.")
    server_socket.listen()
    while(True):
        try:
            clientsocket, addr = server_socket.accept()
            lock = threading.Lock()
            socket_loc_map[clientsocket] = lock
            thread = threading.Thread(
                target=server.handle_client, args=(clientsocket, lock, ))
            thread.start()
            print('Connection created with:', addr)
        except BlockingIOError:
            pass
        finally:
            server.handle_undelivered_messages()
