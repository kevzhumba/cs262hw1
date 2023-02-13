import socket
import protocol
import threading

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
    # Handle ending/disconnecting later
    curr_msg_id = -1
    curr_op = -1
    # represents the bytes from the last recieve that occurred after packet termination; invariant has to be that left_over_packet ALWAYS starts with a header.
    left_over_packet = bytes()
    running_msg = ""
    mdg_id_accum = 0
    while True:
        msg = client.recv(2048)
        if (msg == 0):
            # client disconnected   
            break
        curr_msg_to_parse = left_over_packet + msg
        if (len(curr_msg_to_parse) < METADATA_LENGTH):
            left_over_packet = curr_msg_to_parse
        else:
            # we want to continue the iteration if we ended the last packet
            continue_iteration = True
            while(continue_iteration and len(curr_msg_to_parse) > METADATA_LENGTH):
                # invariant here is that we at least have the metadata available
                md = parse_metadata(curr_msg_to_parse)
                if (not (md.version == VERSION)):
                    # TODO throw response error, also maybe make sure that no packets of the same message id are processed
                    return None
                else:
                    curr_payload_size = md.payload_size
                    if (len(curr_msg_to_parse[10:]) < curr_payload_size):
                        # wait to receive more since we dont have the entire payload yet
                        continue_iteration = False
                    else:
                        # now we have the whole packet, we can parse the data.
                        # parse payload size of the built up msg starting from after the metadata
                        packet_to_parse = curr_msg_to_parse[10: curr_payload_size + 10]
                        incomplete_msg = packet_to_parse.decode('ascii')
                        if (curr_msg_id == md.message_id and curr_op == md.operation_code):
                            running_msg += incomplete_msg
                        else:
                            # else this is a new message
                            running_msg = incomplete_msg
                            curr_msg_id = md.message_id
                        # if running msg is done, then do something based on op codes and such
                        if (running_msg[-1] == '\n'):
                            #TODO do something, set curr msg id to -1
                            msg_id_accum = process_operation(client, socket_lock, md, running_msg, msg_id_accum)
                            curr_msg_id = -1
                            pass
                        # once we've processed the current packet, we want to set the curr_msg_to_parse
                        # to be the rest of the total msg, and then iterate over the total msg to parse again
                        curr_msg_to_parse = curr_msg_to_parse[curr_payload_size+10:]
            left_over_packet = curr_msg_to_parse

def process_operation(client_socket, socket_lock, metadata: protocol.Metadata, msg, id_accum):
    match metadata.operation_code.value:
        #TODO check log in status with operations i.e. cant log in if already logged in, cant create account if already logged in, cant log out if not logged in, 
        # cant send message if not logged in
        case 1: 
            account_name = msg[len("username="):]
            account_list_lock.acquire()
            if (account_name in account_list):
                account_list_lock.release()
                response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Error: Account already exists'})
                send(client_socket, socket_lock, response)
            else:
                account_list.append(account_name)
                account_list_lock.release()
                logged_in_lock.acquire()
                logged_in_user_to_client_socket[account_name] = (client_socket, socket_lock)
                logged_in_lock.release()
                response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Success'})
                send(client_socket, socket_lock, response)
        case 5: 
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
                    account_list_lock.release()
                    undelivered_msg_lock.acquire()
                    if (recipient in undelivered_msg.keys()):
                        undelivered_msg[recipient] = undelivered_msg[recipient] + [(username, message)]
                    else:
                        undelivered_msg[recipient] = [(username, message)]
                    undelivered_msg_lock.release()
        case 7: 
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
        case 9:
            logged_in_lock.acquire()
            if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                logged_in_lock.release()
                response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Already logged into an account, please log off first'})
                send(client_socket, socket_lock, response)
            else:
                account_name = msg[len("username="):]
                account_list_lock.acquire()
                if (not account_name in account_list):
                    account_list_lock.release()
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Account does not exist'})
                    send(client_socket, socket_lock, response)
                elif (account_name in logged_in_user_to_client_socket.keys()):
                    account_list_lock.release()
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Error: Someone else is logged into that account'})
                    send(client_socket, socket_lock, response)
                else:
                    account_list_lock.release()
                    logged_in_user_to_client_socket[account_name] = (client_socket, socket_lock)
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {'status': 'Success'})
                    send(client_socket, socket_lock, response)
        case 11:
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
    return id_accum + 1

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

def handleUndeliveredMessages():
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
            thread = threading.Thread(target=handle_client,args = (clientsocket, lock, ))
            thread.start()
            print('Connected to by:', addr)
        except BlockingIOError:
            pass
        finally:
            handleUndeliveredMessages()

        
        
            

server_soc()
