import socket

HOST = '127.0.0.1'
PORT = 6000


def server_soc():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print("Server Started")
    clientsocket, addr = server_socket.accept()
    print('Connected to by:', addr)

    bdata = clientsocket.recv(128)
    data = bdata.decode('ascii')
