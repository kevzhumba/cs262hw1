import grpc
import threading
from typing import Literal
from time import sleep
import chat_service_pb2
import chat_service_pb2_grpc

std_out_lock = threading.Lock()


def atomic_print(lock, msg, end=None):
    lock.acquire()
    print(msg, end=end)
    lock.release()


class Client:
    def __init__(self, server_stub):
        self.stub = server_stub
        self.username = None

        self.listen_for_messages_flag = True

    def listen_for_messages(self):
        while self.listen_for_messages_flag:
            try:
                got_message = False
                for message in self.stub.GetMessages(chat_service_pb2.GetMessagesRequest()):
                    atomic_print(
                        std_out_lock, f"\nMessage from {message.sender}: {message.message}")
                    got_message = True
                if got_message:
                    atomic_print(std_out_lock, self._get_prompt())
                sleep(0.05)
            except grpc.RpcError as e:
                sleep(1)

    def _get_prompt(self):
        command_line_prefix = f'{self.username} >' if self.username else '>'
        return f"{command_line_prefix} Enter command (type 'help' for list of commands): "

    def run(self):
        # Start listening for messages in a new thread
        self.listen_thread = threading.Thread(
            target=self.listen_for_messages)
        self.listen_thread.start()

        while True:
            try:
                user_input = input(self._get_prompt())
                user_input = user_input.lower().strip()
                match user_input:
                    case 'help':
                        atomic_print(
                            std_out_lock, 'Enter one of the following command numbers: \n1 - Create account \n2 - Login \n3 - List accounts \n4 - Send message \n5 - Logoff \n6 - Delete account')
                    case '1' | 'create account':
                        self._create_account_or_log_in('CREATE_ACCOUNT')
                    case '2' | 'login':
                        self._create_account_or_log_in('LOG_IN')
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
            except KeyboardInterrupt:
                self.listen_for_messages_flag = False
                self._logoff(output_message=False)
                return
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    self.listen_for_messages_flag = False
                    atomic_print(
                        std_out_lock, 'Server is unavailable. Please try again later.')
                    return
                else:
                    self._logoff(output_message=False)
                    atomic_print(
                        std_out_lock, 'An error occurred and you have been logged out.')

    def _create_account_or_log_in(self, action: Literal['CREATE_ACCOUNT', 'LOG_IN']):
        username = input('Enter username: ')
        # Check valid username, only letters and numbers
        if username.strip().isalnum() and 5 <= len(username) <= 20:
            if action == 'CREATE_ACCOUNT':
                response = self.stub.CreateAccount(
                    chat_service_pb2.CreateAccountRequest(username=username))
            else:
                response = self.stub.LogIn(
                    chat_service_pb2.LogInRequest(username=username))
            if response.status == 'Success':
                self.username = username
                atomic_print(std_out_lock, f'Success! Logged in as {username}')
            else:
                atomic_print(std_out_lock, response.status)
        else:
            atomic_print(
                std_out_lock, 'Invalid username. Username must be between 5 and 20 characters and only contain letters and numbers.')

    def _list_accounts(self):
        query = input('Enter query: ')
        response = self.stub.ListAccounts(
            chat_service_pb2.ListAccountsRequest(query=query))
        if response.status == "Success":
            accounts = '\n'.join(response.accounts)
            atomic_print(std_out_lock, f"Account search results:\n{accounts}")
        else:
            atomic_print(std_out_lock, response.status)

    def _send_message(self):
        user = input('Enter recipient username: ')
        user_msg = input('Enter message: ')
        response = self.stub.SendMessage(
            chat_service_pb2.SendMessageRequest(recipient=user, message=user_msg))
        if response.status == "Success":
            atomic_print(std_out_lock, "Message sent successfully.")
        else:
            atomic_print(std_out_lock, response.status)

    def _logoff(self, output_message=True):
        response = self.stub.LogOff(chat_service_pb2.LogOffRequest())
        if response.status == "Success":
            self.username = None
            msg = "You are now logged out."
        else:
            msg = response.status
        if output_message:
            atomic_print(std_out_lock, msg)

    def _delete_account(self):
        response = self.stub.DeleteAccount(
            chat_service_pb2.DeleteAccountRequest())
        if response.status == "Success":
            self.username = None
            atomic_print(
                std_out_lock, "Deleting account successful; you are now logged out.")
        else:
            atomic_print(std_out_lock, response.status)


if __name__ == '__main__':
    host = input('Enter host: ')
    port = int(input('Enter port: '))

    with grpc.insecure_channel(f'{host}:{port}') as channel:
        stub = chat_service_pb2_grpc.ChatServiceStub(channel)
        client = Client(stub)
        print('Connected to server')

        client.run()
