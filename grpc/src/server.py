import threading
import re
from collections import defaultdict

import chat_service_pb2
import chat_service_pb2_grpc


class ChatServiceServicer(chat_service_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.account_list = []  # List of usernames
        self.account_list_lock = threading.Lock()

        self.logged_in = {}  # Map of username to socket ID
        self.logged_in_lock = threading.Lock()

        # Map of recipient username to list of (sender, message) for that recipient
        self.undelivered_msg = defaultdict(list)
        self.undelivered_msg_lock = threading.Lock()

    def _atomicIsLoggedIn(self, client_socket):
        self.logged_in_lock.acquire()
        ret = client_socket in self.logged_in.values()
        self.logged_in_lock.release()
        return ret

    def _atomicLogIn(self, client_socket, account_name):
        self.logged_in_lock.acquire()
        self.logged_in[account_name] = client_socket
        self.logged_in_lock.release()

    def _atomicIsAccountCreated(self, recipient):
        self.account_list_lock.acquire()
        ret = recipient in self.account_list
        self.account_list_lock.release()
        return ret

    def CreateAccount(self, request, context):
        username = request.username
        client_socket = context.peer()
        if self._atomicIsLoggedIn(client_socket):
            status = 'Error: User can\'t create an account while logged in.'
        else:
            self.account_list_lock.acquire()
            if (username in self.account_list):
                self.account_list_lock.release()
                status = 'Error: Account already exists.'
            else:
                self.account_list.append(username)
                # accountLock > login
                self._atomicLogIn(client_socket, username)
                # if we release the lock earlier, someone else can create the same acccount and try to log in while we wait for the log in lock
                self.account_list_lock.release()
                print("Account created: ", username)

                status = 'Success'
        return chat_service_pb2.CreateAccountResponse(status=status, username=username)

    def ListAccounts(self, request, context):
        try:
            pattern = re.compile(
                fr"{request.query}", flags=re.IGNORECASE)
            self.account_list_lock.acquire()
            accounts = []
            for account in self.account_list:
                if pattern.match(account):
                    accounts.append(account)
            self.account_list_lock.release()
            status = 'Success'
        except:
            status = 'Error: regex is malformed.'
            accounts = []

        return chat_service_pb2.ListAccountsResponse(status=status, accounts=accounts)

    def SendMessage(self, request, context):
        # in this case we want to add to undelivered messages, which the server iterator will figure out i think
        # here we check the person sending is logged in and the recipient account has been created
        self.logged_in_lock.acquire()
        client_socket = context.peer()
        if client_socket not in self.logged_in.values():
            self.logged_in_lock.release()
            status = 'Error: Need to be logged in to send a message.'
        else:
            username = [k for k, v in self.logged_in.items() if v ==
                        client_socket][0]
            self.logged_in_lock.release()
            recipient = request.recipient
            message = request.message
            self.account_list_lock.acquire()
            if recipient not in self.account_list:
                self.account_list_lock.release()
                status = 'Error: The recipient of the message does not exist.'
            else:
                self.undelivered_msg_lock.acquire()
                self.undelivered_msg[recipient].append((username, message))
                self.undelivered_msg_lock.release()
                # ACCOUNT LIST > UNDELIVERED MSG)
                self.account_list_lock.release()
                status = 'Success'
                print(f"Queued message from {username} to {recipient}")

        return chat_service_pb2.SendMessageResponse(status=status)

    def GetMessages(self, request, context):
        client_socket = context.peer()
        self.logged_in_lock.acquire()
        if client_socket in self.logged_in.values():
            username = [k for k, v in self.logged_in.items() if v ==
                        client_socket][0]
            while True:
                deliver_msg = False
                self.undelivered_msg_lock.acquire()
                if len(self.undelivered_msg[username]):
                    deliver_msg = True
                    sender, msg = self.undelivered_msg[username].pop(0)
                self.undelivered_msg_lock.release()
                if deliver_msg:
                    print(f"Sending messages to {username}")
                    yield chat_service_pb2.ChatMessage(sender=sender, message=msg)
                else:
                    break
        self.logged_in_lock.release()

    def DeleteAccount(self, request, context):
        self.logged_in_lock.acquire()
        client_socket = context.peer()
        if client_socket in self.logged_in.values():
            username = [k for k, v in self.logged_in.items() if v ==
                        client_socket][0]
            self.logged_in.pop(username)
            self.logged_in_lock.release()
            self.account_list_lock.acquire()
            self.account_list.remove(username)
            self.account_list_lock.release()
            status = 'Success'
            print("Account deleted: ", username)
        else:
            self.logged_in_lock.release()
            status = 'Error: Need to be logged in to delete your account.'

        return chat_service_pb2.DeleteAccountResponse(status=status)

    def LogIn(self, request, context):
        client_socket = context.peer()
        username = request.username
        self.logged_in_lock.acquire()
        if client_socket in self.logged_in.values():
            self.logged_in_lock.release()
            status = 'Error: Already logged into an account, please log off first.'
        else:
            if (not self._atomicIsAccountCreated(username)):
                self.logged_in_lock.release()
                status = 'Error: Account does not exist.'
            elif username in self.logged_in.keys():
                self.logged_in_lock.release()
                status = 'Error: Someone else is logged into that account.'
            else:
                self.logged_in[username] = client_socket
                self.logged_in_lock.release()
                status = 'Success'
                print("Logged in: ", username)

        return chat_service_pb2.LogInResponse(status=status, username=username)

    def LogOff(self, request, context):
        self.logged_in_lock.acquire()
        client_socket = context.peer()
        if client_socket in self.logged_in.values():
            username = [k for k, v in self.logged_in.items() if v ==
                        client_socket][0]
            self.logged_in.pop(username)
            self.logged_in_lock.release()
            status = 'Success'
            print("Logged off: ", username)
        else:
            self.logged_in_lock.release()
            status = 'Error: Need to be logged in to log out of your account.'

        return chat_service_pb2.LogOffResponse(status=status)
