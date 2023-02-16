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
            
            thread = threading.Thread(target=listen_to_server, args=(self.socket, ))
            thread.start()
            print('Connected to server')
        except:
            raise ConnectionError('Connection failed')
        
    def disconnect(self):
        self.socket.close()
    
    def run(self):
        while True:
            user_input = input("Enter command (type 'help' for list of commands): ")
            user_input = user_input.lower().strip()
            match user_input:
                case 'help':
                    std_out_lock.acquire()
                    print('List of commands: \nCreate account: 1 \nLogin: 2 \nList accounts: 3 \nSend message: 4 \nLogoff: 5 \nDelete account: 6')
                case '1' | 'create account':
                    self._login_or_create_account('CREATE_ACCOUNT')
                case '2' | 'login': 
                    self._login_or_create_account('LOG_IN')
                case '3' | 'list accounts':
                    pass
                case '4' | 'send message':
                    pass
                case '5' | 'logoff' | 'exit':
                    pass
                case '6' | 'delete account':
                    pass
    
    def _login_or_create_account(self, action: Literal['LOG_IN', 'CREATE_ACCOUNT']):
        # TODO: check validity of username
        username = input('Enter username: ')
        message = protocol.protocol_instance.encode(action, self.message_counter, {'username': username})
        self.socket.send(message)
        
    def _list_accounts(self):
        pass
    
        
def listen_to_server(client):
    protocol.protocol_instance.read_packets(client, process_operation_curry(std_out_lock))

def process_operation_curry(out_lock):
    def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
         match metadata.operation_code.value:
             case 2: #Create account response
                args = protocol.protocol_instance.parse_data(msg)
                if args['status'] == "Success":
                    std_out_lock.acquire()
                    
             case 4: #list accounts response
                 pass
             case 6: #Send message response
                 pass
             case 8: #Delete Account response
                 pass
             case 10: #LOGIN
                 pass
             case 12: #LOGOFF
                 pass
             case 13: #Receive message
    return process_operation
