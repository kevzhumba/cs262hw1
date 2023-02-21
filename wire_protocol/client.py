import socket
from time import sleep
import protocol
import threading
from typing import Literal

std_out_lock = threading.Lock()


class Client:
    def __init__(self, server_host, port, protocol):
        self.server_host = server_host
        self.port = port
        self.protocol = protocol
        self.message_counter = 0
        self.username = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.port))

            # Create a thread to listen continuously listen to server and respond to server messages
            thread = threading.Thread(target=self.listen_to_server, daemon=True)
            thread.start()
            print('Connected to server')
        except:
            raise ConnectionError('Connection failed')

    def disconnect(self):
        self.socket.close()

    def listen_to_server(self):
        self.protocol.read_packets(
            self.socket, self.process_operation_curry(std_out_lock))

    def _get_prompt(self):
        command_line_prefix = f'{self.username} >' if self.username else '>'
        return f"{command_line_prefix} Enter command (type 'help' for list of commands): "

    def run(self):
        # Core user interface loop
        while True:
            user_input = input(self._get_prompt())
            user_input = user_input.lower().strip()
            match user_input:
                case 'help':
                    atomic_print(
                        std_out_lock, 'Enter one of the following command numbers: \n1 - Create account \n2 - Login \n3 - List accounts \n4 - Send message \n5 - Logoff \n6 - Delete account')
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
            sleep(0.2)

    def _login_or_create_account(self, action: Literal['LOG_IN', 'CREATE_ACCOUNT']):
        username = input('Enter username: ')
        # Check valid username, only letters and numbers
        if username.strip().isalnum() and 5 <= len(username) <= 20:
            message = self.protocol.encode(
                action, self.message_counter, {'username': username})
            self.message_counter += 1
            self.protocol.send(self.socket, message)
        else:
            atomic_print(
                std_out_lock, 'Invalid username. Username must be between 5 and 20 characters and only contain letters and numbers.')

    def _list_accounts(self):
        # Send list accounts query
        query = input('Enter query: ')
        message = self.protocol.encode(
            'LIST_ACCOUNTS', self.message_counter, {'query': query})
        self.message_counter += 1
        self.protocol.send(self.socket, message)

    def _send_message(self):
        # Get recipient username and message and send
        user = input('Enter recipient username: ')
        user_msg = input('Enter message: ')
        message = self.protocol.encode(
            'SEND_MESSAGE', self.message_counter, {'recipient': user, 'message': user_msg})
        self.message_counter += 1
        self.protocol.send(self.socket, message)

    def _logoff(self):
        message = self.protocol.encode(
            'LOG_OFF', self.message_counter)
        self.message_counter += 1
        self.protocol.send(self.socket, message)

    def _delete_account(self):
        message = self.protocol.encode(
            'DELETE_ACCOUNT', self.message_counter)
        self.message_counter += 1
        self.protocol.send(self.socket, message)

    def process_operation_curry(self, out_lock):
        def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
            operation_code = metadata.operation_code.value
            args = self.protocol.parse_data(operation_code, msg)
            atomic_print(out_lock, '')
            match operation_code:
                case 2:  # Create account response
                    if args['status'] == "Success":
                        self.username = args['username']
                        atomic_print(
                            out_lock, "Account creation successful. You are now logged in.")
                    else:
                        atomic_print(out_lock, args['status'])
                case 4:  # List accounts response
                    if args['status'] == "Success":
                        atomic_print(
                            out_lock, f"Account search results:\n{args['accounts']}")
                    else:
                        atomic_print(out_lock, args['status'])
                case 6:  # Send message response
                    if not args['status'] == "Success":
                        atomic_print(out_lock, args['status'])
                case 8:  # Delete Account response
                    if args['status'] == "Success":
                        self.username = None
                        atomic_print(
                            out_lock, "Deleting account successful; you are now logged out.")
                    else:
                        atomic_print(out_lock, args['status'])
                case 10:  # Login response
                    if args['status'] == "Success":
                        self.username = args['username']
                        atomic_print(out_lock, "You are now logged in.")
                    else:
                        atomic_print(out_lock, args['status'])
                case 12:  # Logoff response
                    if args['status'] == "Success":
                        self.username = None
                        atomic_print(out_lock, "You are now logged out.")
                    else:
                        atomic_print(out_lock, args['status'])
                case 13:  # Receive message
                    atomic_print(
                        out_lock, f"Message from {args['sender']}: {args['message']} \n\n{self._get_prompt()}")
        return process_operation


def atomic_print(lock, msg, end=None):
    lock.acquire()
    print(msg, end=end)
    lock.release()
