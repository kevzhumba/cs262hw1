import socket

HOST = '127.0.0.1'
PORT = 6000


def client_soc():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    msg = 'Hello, World!'
    bmsg = msg.encode('ascii')
    sent = client_socket.send(bmsg)
    print('Message sent, %d/%d bytes transmitted' % (sent, len(msg)))
    client_socket.close()
