import socket
import protocol
import threading
from typing import Literal

std_out_lock = threading.Lock()


class Client:
    def __init__(self, server_host, port):
        self.server_host = server_host
        self.port = port
        self.message_counter = 0
        self.username = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.port))

            thread = threading.Thread(
                target=listen_to_server, args=(self, ))
            thread.start()
            print('Connected to server')
        except:
            raise ConnectionError('Connection failed')

    def disconnect(self):
        self.socket.close()

    def run(self):
        while True:
            user_input = input(
                "Enter command (type 'help' for list of commands): ")
            user_input = user_input.lower().strip()
            match user_input:
                case 'help':
                    atomic_print(
                        std_out_lock, 'List of commands: \nCreate account: 1 \nLogin: 2 \nList accounts: 3 \nSend message: 4 \nLogoff: 5 \nDelete account: 6')
                case '1' | 'create account':
                    self._login_or_create_account('CREATE_ACCOUNT')
                case '2' | 'login':
                    self._login_or_create_account('LOG_IN')
                case '3' | 'list accounts':
                    self._list_accounts()
                case '4' | 'send message':
                    self._send_message()
                case '5' | 'logoff' | 'exit':
                    self._logoff()
                case '6' | 'delete account':
                    self._delete_account()
                case _:
                    atomic_print(std_out_lock, 'Invalid command')

    def _login_or_create_account(self, action: Literal['LOG_IN', 'CREATE_ACCOUNT']):
        username = input('Enter username: ')
        # Check valid username, only letters and numbers
        if username.strip().isalnum() and 5 <= len(username) <= 20:
            message = protocol.protocol_instance.encode(
                action, self.message_counter, {'username': username})
            self.message_counter += 1
            protocol.protocol_instance.send(self.socket, message)
        else:
            atomic_print(
                std_out_lock, 'Invalid username. Username must be between 5 and 20 characters and only contain letters and numbers.')

    def _list_accounts(self):
        query = input('Enter query: ')
        message = protocol.protocol_instance.encode(
            'LIST_ACCOUNTS', self.message_counter, {'query': query})
        self.message_counter += 1
        protocol.protocol_instance.send(self.socket, message)

    def _send_message(self):
        user = input('Enter recipient username: ')
        user_msg = input('Enter message: ')
        message = protocol.protocol_instance.encode(
            'SEND_MESSAGE', self.message_counter, {'recipient': user, 'message': user_msg})
        self.message_counter += 1
        protocol.protocol_instance.send(self.socket, message)

    def _logoff(self):
        message = protocol.protocol_instance.encode(
            'LOG_OFF', self.message_counter)
        self.message_counter += 1
        protocol.protocol_instance.send(self.socket, message)

    def _delete_account(self):
        message = protocol.protocol_instance.encode(
            'DELETE_ACCOUNT', self.message_counter)
        self.message_counter += 1
        protocol.protocol_instance.send(self.socket, message)

    def process_operation_curry(self, out_lock):
        def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
            args = protocol.protocol_instance.parse_data(msg)
            match metadata.operation_code.value:
                case 2:  # Create account response
                    if args['status'] == "Success":
                        self.username = args['username']
                        atomic_print(
                            out_lock, "Account creation successful. You are now logged in")
                    else:
                        atomic_print(out_lock, args['status'])
                case 4:  # list accounts response
                    if args['status'] == "Success":
                        atomic_print(
                            out_lock, f"The account list is {args['accounts']}")
                    else:
                        atomic_print(out_lock, args['status'])
                case 6:  # Send message response
                    if not args['status'] == "Success":
                        atomic_print(out_lock, args['status'])
                case 8:  # Delete Account response
                    if args['status'] == "Success":
                        self.username = None
                        atomic_print(
                            out_lock, "Deleting account successful; you are now logged out")
                    else:
                        atomic_print(out_lock, args['status'])
                case 10:  # LOGIN
                    if args['status'] == "Success":
                        self.username = args['username']
                        atomic_print(out_lock, "You are now logged in")
                    else:
                        atomic_print(out_lock, args['status'])
                case 12:  # LOGOFF
                    if args['status'] == "Success":
                        self.username = None
                        atomic_print(out_lock, "You are now logged out")
                    else:
                        atomic_print(out_lock, args['status'])
                case 13:  # Receive message
                    atomic_print(
                        out_lock, f"From {args['sender']}: {args['message']}")
        return process_operation


def listen_to_server(client: Client):
    protocol.protocol_instance.read_packets(
        client.socket, client.process_operation_curry(std_out_lock))


def atomic_print(lock, msg):
    lock.acquire()
    print(msg)
    lock.release()
