import socket
from time import sleep
import time
import protocol
import threading
import re
import logging


class Server:
    def __init__(self, host, port, protocol):
        self.host = host
        self.port = port

        self.msg_counter = 0

        self.account_list = []  # List of usernames
        self.account_list_lock = threading.Lock()

        self.logged_in = {}  # Map of username to (client_socket, socket lock)
        self.logged_in_lock = threading.Lock()

        # Map of recipient username to list of (sender, message) for that recipient
        self.undelivered_msg = {}
        self.undelivered_msg_lock = threading.Lock()

        self.protocol = protocol

    def disconnect(self):
        self.socket.close()

    def handle_client(self, client, socket_lock):
        """Function to handle a client on a single thread, which continuously reads the socket and processes the messages

        Args:
            client (socket.socket): The socket to read from.
            socket_lock (threading.Lock): Lock to prevent concurrent socket read
        """
        value = self.protocol.read_packets(
            client, self.process_operation_curried(socket_lock))
        if value is None:
            client.close()
        self.logged_in_lock.acquire()
        username = [k for k, v in self.logged_in.items() if v == (
            client, socket_lock)]
        if len(username) > 0:
            self.logged_in.pop(username[0])
        self.logged_in_lock.release()
        print("Closing client.")

    def atomicIsLoggedIn(self, client_socket, socket_lock):
        """Atomically checks if the client is logged in 

        Args:
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        ret = True
        self.logged_in_lock.acquire()
        if (client_socket, socket_lock) not in self.logged_in.values():
            ret = False
        self.logged_in_lock.release()
        return ret

    def atomicLogIn(self, client_socket, socket_lock, account_name):
        """Atomically logs client in with the account name

        Args:
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
            account_name (str): The account name to log in
        """
        self.logged_in_lock.acquire()
        self.logged_in[account_name] = (
            client_socket, socket_lock)
        self.logged_in_lock.release()

    def atomicIsAccountCreated(self, recipient):
        """Atomically checks if an account is created

        Args:
            recipient (str): The account name to check
        """
        ret = True
        self.account_list_lock.acquire()
        ret = recipient in self.account_list
        self.account_list_lock.release()
        return ret

    def process_create_account(self, args, client_socket, socket_lock):
        """Processes a create account request. We require that the requester is not 
        logged in and that the account doesn't exist

        Args:
            args (dict): The args object for creating an account parsed from the received message
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        account_name = args["username"]
        if self.atomicIsLoggedIn(client_socket, socket_lock):
            response = {
                'status': 'Error: User can\'t create an account while logged in.', 'username': account_name}
        else:
            self.account_list_lock.acquire()
            if (account_name in self.account_list):
                self.account_list_lock.release()
                response = {
                    'status': 'Error: Account already exists.', 'username': account_name}
            else:
                self.account_list.append(account_name)
                self.atomicLogIn(client_socket, socket_lock,
                                 account_name)  # accountLock > login
                # if we release the lock earlier, someone else can create the same acccount and try to log in while we wait for the log in lock
                self.account_list_lock.release()
                print("Account created: " + account_name)
                response = {'status': 'Success', 'username': account_name}
        return response

    def process_list_accounts(self, args):
        """Processes a list account request. We don't require the requester to be logged in.

        Args:
            account_name (str): The args object for creating an account parsed from the received message
        """
        logging.info('Received', time.time())
        try:
            pattern = re.compile(
                fr"{args['query']}", flags=re.IGNORECASE)
            self.account_list_lock.acquire()
            result = []
            for account in self.account_list:
                if pattern.match(account):
                    result.append(account)
            self.account_list_lock.release()
            response = {'status': 'Success', 'accounts': ";".join(result)}
        except:
            response = {'status': 'Error: regex is malformed.', 'accounts': ''}
        finally:
            return response

    def process_send_msg(self, args, client_socket, socket_lock):
        """Processes a send message request. We require that the requester is 
        logged in and the recipient exists.

        Args:
            args (dict): The args object for sending a message
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        self.logged_in_lock.acquire()
        if (not (client_socket, socket_lock) in self.logged_in.values()):
            self.logged_in_lock.release()
            response = {
                'status': 'Error: Need to be logged in to send a message.'}
        else:
            username = [k for k, v in self.logged_in.items() if v == (
                client_socket, socket_lock)][0]
            self.logged_in_lock.release()
            recipient = args["recipient"]
            message = args["message"]
            print("sending message", recipient, message)
            self.account_list_lock.acquire()
            if recipient not in self.account_list:
                self.account_list_lock.release()
                response = {
                    'status': 'Error: The recipient of the message does not exist.'}
            else:
                self.undelivered_msg_lock.acquire()
                if recipient in self.undelivered_msg:
                    self.undelivered_msg[recipient] += [
                        (username, message)]
                else:
                    self.undelivered_msg[recipient] = [
                        (username, message)]
                self.undelivered_msg_lock.release()
                self.account_list_lock.release()
                response = {'status': 'Success'}
        return response

    def process_delete_account(self, client_socket, socket_lock):
        """Processes a delete account request. We require that the requester is 
        logged in.

        Args:
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        self.logged_in_lock.acquire()

        if ((client_socket, socket_lock) in self.logged_in.values()):
            username = [k for k, v in self.logged_in.items() if v == (
                client_socket, socket_lock)][0]
            self.logged_in.pop(username)
            self.logged_in_lock.release()
            self.account_list_lock.acquire()
            self.account_list.remove(username)
            self.account_list_lock.release()
            response = {'status': 'Success'}
        else:
            self.logged_in_lock.release()
            response = {
                'status': 'Error: Need to be logged in to delete your account.'}
        return response

    def process_login(self, args, client_socket, socket_lock):
        """Processes a login request. We require that the requester is 
        not logged in, the account exists, and no one else is logged into the account.

        Args:
            args (dict): The args object for sending a message
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        self.logged_in_lock.acquire()
        if ((client_socket, socket_lock) in self.logged_in.values()):
            self.logged_in_lock.release()
            response = {
                'status': 'Error: Already logged into an account, please log off first.', 'username': ''}
        else:
            account_name = args['username']
            if (not self.atomicIsAccountCreated(account_name)):
                self.logged_in_lock.release()
                response = {
                    'status': 'Error: Account does not exist.', 'username': account_name}
            elif (account_name in self.logged_in.keys()):
                self.logged_in_lock.release()
                response = {
                    'status': 'Error: Someone else is logged into that account.', 'username': account_name}
            else:
                self.logged_in[account_name] = (
                    client_socket, socket_lock)
                self.logged_in_lock.release()
                response = {'status': 'Success', 'username': account_name}
        return response

    def process_logoff(self, client_socket, socket_lock):
        """Processes a logoff request. We require that the requester is 
        logged in.

        Args:
            client (socket.socket): The client socket
            socket_lock (threading.Lock): The socket's associated lock
        """
        self.logged_in_lock.acquire()
        if ((client_socket, socket_lock) in self.logged_in.values()):
            username = [k for k, v in self.logged_in.items() if v == (
                client_socket, socket_lock)][0]
            self.logged_in.pop(username)
            self.logged_in_lock.release()
            response = {'status': 'Success'}
        else:
            self.logged_in_lock.release()
            response = {
                'status': 'Error: Need to be logged in to log out of your account.'}
        return response

    def process_operation_curried(self, socket_lock):
        """Processes the operation. This is a curried function to work with the 
        read packets api provided in protocol. See the relevant process functions
        for functionality.

        Args:
            socket_lock (threading.Lock): The socket's associated lock
        """
        def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
            """Processes the operation. See the relevant process functions
            for functionality.

            Args:
                client (socket.socket): The client socket
                metadata (protocol.Metadata): The metadata parsed from the message
                msg (str): message to parse for operation arguments
                id_accum (it): integer accumulator for message 
            """
            operation_code = metadata.operation_code.value
            args = self.protocol.parse_data(operation_code, msg)
            match operation_code:
                case 1:  # CREATE_ACCOUNT
                    response = self.protocol.encode(
                        'CREATE_ACCOUNT_RESPONSE', id_accum, self.process_create_account(args, client_socket, socket_lock))
                case 3:  # LIST ACCOUNTS
                    response = self.protocol.encode(
                        'LIST_ACCOUNTS_RESPONSE', id_accum, self.process_list_accounts(args))
                case 5:  # SENDMSG
                    # in this case we want to add to undelivered messages, which the server iterator will figure out i think
                    # here we check the person sending is logged in and the recipient account has been created
                    response = self.protocol.encode(
                        'SEND_MESSAGE_RESPONSE', id_accum, self.process_send_msg(args, client_socket, socket_lock))
                case 7:  # DELETE
                    response = self.protocol.encode(
                        'DELETE_ACCOUNT_RESPONSE', id_accum, self.process_delete_account(client_socket, socket_lock))
                case 9:  # LOGIN
                    response = self.protocol.encode(
                        'LOG_IN_RESPONSE', id_accum, self.process_login(args, client_socket, socket_lock))
                case 11:  # LOGOFF
                    response = self.protocol.encode(
                        'LOG_OFF_RESPONSE', id_accum, self.process_logoff(client_socket, socket_lock))
            if not response is None:
                self.protocol.send(client_socket, response, socket_lock)
        return process_operation

    def handle_undelivered_messages(self):
        """Sends any undelivered messages to the recipients. If the recipient is not logged in
        or sending fails, the undelivered message remains on the work queue. 
        """
        self.undelivered_msg_lock.acquire()
        for recipient, message_infos in self.undelivered_msg.items():
            self.logged_in_lock.acquire()
            if recipient in self.logged_in:
                client_socket, socket_lock = self.logged_in[recipient]
                undelivered_messages = []
                for (sender, msg) in message_infos:
                    response = self.protocol.encode(
                        "RECV_MESSAGE", self.msg_counter, {"sender": sender, "message": msg})
                    status = self.protocol.send(
                        client_socket, response, socket_lock)
                    if not status:
                        undelivered_messages.append((sender, msg))
                    self.msg_counter = self.msg_counter + 1
                self.undelivered_msg[recipient] = undelivered_messages
            self.logged_in_lock.release()
        self.undelivered_msg_lock.release()

    def send_messages(self):
        """ Handles undelivered messages in a loop, and sleeps to provide better 
        responsiveness on the client side
        """
        while True:
            self.handle_undelivered_messages()
            sleep(0.01)

    def run(self):
        """ Runs the server by starting the message delivery thread. It then
        accepts any connections and spawns a new thread to handle the connection
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = server_socket
        server_socket.setblocking(0)
        server_socket.bind((self.host, self.port))
        print("Server started.")
        server_socket.listen()

        message_delivery_thread = threading.Thread(
            target=self.send_messages, daemon=True)
        message_delivery_thread.start()
        while(True):
            try:
                clientsocket, addr = server_socket.accept()
                clientsocket.setblocking(1)
                lock = threading.Lock()
                thread = threading.Thread(
                    target=self.handle_client, args=(clientsocket, lock, ), daemon=True)
                thread.start()
                print('Connection created with:', addr)
            except BlockingIOError:
                pass
            finally:
                self.handle_undelivered_messages()
