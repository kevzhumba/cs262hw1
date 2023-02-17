import socket
import protocol
import threading
import re

HOST = '127.0.0.1'
PORT = 6000
METADATA_LENGTH = 10
VERSION = 1

account_list = []
account_list_lock = threading.Lock()
logged_in_user_to_client_socket = {}
logged_in_lock = threading.Lock()
undelivered_msg = {}
undelivered_msg_lock = threading.Lock()
msg_accum = 0

def handle_client(client, socket_lock):
    protocol.protocol_instance.read_packets(client, process_operation_curried(socket_lock)) 

def atomicIsLoggedIn(client_socket, socket_lock):
    ret = True
    logged_in_lock.acquire()
    if (not (client_socket, socket_lock) in logged_in_user_to_client_socket.values):
        ret = False
    logged_in_lock.release()
    return ret

def atomicLogIn(client_socket, socket_lock, account_name):
    logged_in_lock.acquire()
    logged_in_user_to_client_socket[account_name] = (client_socket, socket_lock)
    logged_in_lock.release()

def atomicIsAccountCreated(recipient):
    ret = True
    account_list_lock.acquire()
    ret = recipient in account_list
    account_list_lock.release()
    return ret

def process_operation_curried(socket_lock):
    def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
        match metadata.operation_code.value:
            #TODO check log in status with operations i.e. cant log in if already logged in, cant create account if already logged in, cant log out if not logged in, 
            # cant send message if not logged in
            case 1: #LOGIN
                account_name = msg[len("username="):]
                if (atomicIsLoggedIn(client_socket, socket_lock)):
                    response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Error: User can\'t create an account while logged in'})
                    send(client_socket, socket_lock, response)
                else:
                    account_list_lock.acquire()
                    if (account_name in account_list):
                        account_list_lock.release()
                        response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Error: Account already exists'})
                        send(client_socket, socket_lock, response)
                    else:
                        account_list.append(account_name)
                        atomicLogIn(client_socket, socket_lock, account_name) #accountLock > login
                        account_list_lock.release() #if we release the lock earlier, someone else can create the same acccount and try to log in while we wait for the log in lock
                        response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Success'})
                        send(client_socket, socket_lock, response)
            case 3: 
                args = protocol.protocol_instance.parse_data(msg)
                try:
                    pattern = re.compile(args['query'])
                    account_list_lock.acquire()
                    result = []
                    for account in account_list:
                        if pattern.match(account):
                            result.append(account)
                    account_list_lock.release()
                    response = protocol.protocol_instance.encode('LIST_ACCOUNTS_RESPONSE', id_accum, {'status': 'Success', 'account' : "; ".join(result)})
                    send(client_socket, socket_lock, response)
                except:
                    response = protocol.protocol_instance.encode('LIST_ACCOUNTS_RESPONSE', id_accum, {'status': 'Error: regex is malformed'})
                    send(client_socket, socket_lock, response)

            case 5: #SENDMSG
                # in this case we want to add to undelivered messages, which the server iterator will figure out i think
                # here we check the person sending is logged in and the recipient account has been created
                logged_in_lock.acquire()
                if (not (client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('SEND_MESSAGE_RESPONSE', id_accum, {'status': 'Error: Need to be logged in to send a message'})
                    send(client_socket, socket_lock, response)
                else:
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (client_socket, socket_lock)][0]
                    logged_in_lock.release()
                    args = msg.split('\r')
                    recipient = args[0][len("recipient="): ]
                    message = args[1][len("message="):]
                    account_list_lock.acquire()
                    if (not recipient in account_list):
                        account_list_lock.release()
                        response = protocol.protocol_instance.encode('SEND_MESSAGE_RESPONSE', id_accum, {'status': 'Error: The recipient of the message does not exist'})
                        send(client_socket, socket_lock, response)
                    else:
                        undelivered_msg_lock.acquire()
                        if (recipient in undelivered_msg.keys()):
                            undelivered_msg[recipient] = undelivered_msg[recipient] + [(username, message)]
                        else:
                            undelivered_msg[recipient] = [(username, message)]
                        undelivered_msg_lock.release()
                        account_list_lock.release() #ACCOUNT LIST > UNDELIVERED MSG

            case 7: #DELETE
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (client_socket, socket_lock)][0]
                    logged_in_user_to_client_socket.pop(username)
                    logged_in_lock.release()
                    account_list_lock.acquire()
                    account_list.remove(username)
                    account_list_lock.release()
                    response = protocol.protocol_instance.encode('DELETE_ACCOUNT_RESPONSE', id_accum, {'status': 'Success'})
                    send(client_socket, socket_lock, response)
                else:
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('DELETE_ACCOUNT_RESPONSE', id_accum, {'status': 'Error: Need to be logged in to delete your account'})
                    send(client_socket, socket_lock, response)
            case 9: #LOGIN
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Already logged into an account, please log off first'})
                    send(client_socket, socket_lock, response)
                else:
                    account_name = msg[len("username="):]
                    if (not atomicIsAccountCreated(account_name)):
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Account does not exist'})
                        send(client_socket, socket_lock, response)
                    elif (account_name in logged_in_user_to_client_socket.keys()):
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Someone else is logged into that account'})
                        send(client_socket, socket_lock, response)
                    else:
                        logged_in_user_to_client_socket[account_name] = (client_socket, socket_lock)
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Success'})
                        send(client_socket, socket_lock, response)
            case 11: #LOGOFF
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (client_socket, socket_lock)][0]
                    logged_in_user_to_client_socket.pop(username)
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_OFF_RESPONSE', id_accum, {'status': 'Success'})
                    send(client_socket, socket_lock, response)
                else:
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_OFF_RESPONSE', id_accum, {'status': 'Error: Need to be logged in to log out of your account'})
                    send(client_socket, socket_lock, response)
    return process_operation

def send(client_socket, socket_lock, msg):
    socket_lock.acquire()         
    accum = 0
    targetSize = len(msg)
    while (not accum == targetSize):
        sent = client_socket.send(msg, 2048)
        if (sent == 0):
            #TODO handle correctly
            socket_lock.release()
            raise RuntimeError("socket connection broken")
        accum += sent
    socket_lock.release()      


def parse_metadata(bytes) -> protocol.Metadata:
    '''
        Takes in a bytes object and parses the metadata. 
    '''
    # bytes is the result of client recv
    # idx is the byte index into the metadata we are currently readin
    return protocol.Metadata(bytes[0:1], bytes[1:2], bytes[2:3], bytes[3:6], bytes[6:8], bytes[8:10])

def handle_undelivered_messages():
    undelivered_msg_lock.acquire()
    for (k,v) in undelivered_msg.items():
        logged_in_lock.acquire()
        if (k in logged_in_user_to_client_socket):
            (client_socket, socket_lock) = logged_in_user_to_client_socket(k)
            for (sender, msg) in v:
                response = protocol.protocol_instance.encode("RECV_MESSAGE", msg_accum, {"sender": k, "message": msg})
                send(client_socket, socket_lock, response)
        logged_in_lock.release()
    undelivered_msg_lock.release()

def server_soc():
    print("YES")
    socket_loc_map = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(0)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    while(True):
        try:
            clientsocket, addr = server_socket.accept()
            lock = threading.Lock()
            socket_loc_map[clientsocket] = lock
            thread = threading.Thread(target=handle_client, args=(clientsocket, lock, ))
            thread.start()
            print('Connection created with:', addr)
        except BlockingIOError:
            pass
        finally:
            handle_undelivered_messages()

        
        
            

server_soc()
