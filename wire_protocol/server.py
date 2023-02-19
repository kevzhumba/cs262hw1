import socket
import protocol
import threading
import re

account_list = []
account_list_lock = threading.Lock()
logged_in_user_to_client_socket = {}
logged_in_lock = threading.Lock()
undelivered_msg = {}
undelivered_msg_lock = threading.Lock()
msg_accum = 0


def handle_client(client, socket_lock):
    protocol.protocol_instance.read_packets(
        client, process_operation_curried(socket_lock))


def atomicIsLoggedIn(client_socket, socket_lock):
    ret = True
    logged_in_lock.acquire()
    if (client_socket, socket_lock) not in logged_in_user_to_client_socket.values():
        ret = False
    logged_in_lock.release()
    return ret


def atomicLogIn(client_socket, socket_lock, account_name):
    logged_in_lock.acquire()
    logged_in_user_to_client_socket[account_name] = (
        client_socket, socket_lock)
    logged_in_lock.release()


def atomicIsAccountCreated(recipient):
    ret = True
    account_list_lock.acquire()
    ret = recipient in account_list
    account_list_lock.release()
    return ret


def process_operation_curried(socket_lock):
    def process_operation(client_socket, metadata: protocol.Metadata, msg, id_accum):
        operation_code = metadata.operation_code.value
        print(msg)
        args = protocol.protocol_instance.parse_data(operation_code, msg)
        match operation_code:
            # TODO check log in status with operations i.e. cant log in if already logged in, cant create account if already logged in, cant log out if not logged in,
            # cant send message if not logged in
            case 1:  # CREATE_ACCOUNT
                account_name = args["username"]
                if atomicIsLoggedIn(client_socket, socket_lock):
                    response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {
                                                                 'status': 'Error: User can\'t create an account while logged in.', 'username': account_name})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                else:
                    account_list_lock.acquire()
                    if (account_name in account_list):
                        account_list_lock.release()
                        response = protocol.protocol_instance.encode('CREATE_ACCOUNT_RESPONSE', id_accum, {
                                                                     'status': 'Error: Account already exists.', 'username': account_name})
                        protocol.protocol_instance.send(
                            client_socket, response, socket_lock)
                    else:
                        account_list.append(account_name)
                        atomicLogIn(client_socket, socket_lock,
                                    account_name)  # accountLock > login
                        # if we release the lock earlier, someone else can create the same acccount and try to log in while we wait for the log in lock
                        account_list_lock.release()
                        print("Account created: " + account_name)
                        response = protocol.protocol_instance.encode(
                            'CREATE_ACCOUNT_RESPONSE', id_accum, {'status': 'Success', 'username': account_name})
                        protocol.protocol_instance.send(
                            client_socket, response, socket_lock)
            case 3:  # LIST ACCOUNTS
                try:
                    pattern = re.compile(args['query'])
                    account_list_lock.acquire()
                    result = []
                    for account in account_list:
                        if pattern.match(account):
                            result.append(account)
                    account_list_lock.release()
                    response = protocol.protocol_instance.encode('LIST_ACCOUNTS_RESPONSE', id_accum, {
                                                                 'status': 'Success', 'account': "; ".join(result)})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                except:
                    response = protocol.protocol_instance.encode('LIST_ACCOUNTS_RESPONSE', id_accum, {
                                                                 'status': 'Error: regex is malformed.'})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)

            case 5:  # SENDMSG
                # in this case we want to add to undelivered messages, which the server iterator will figure out i think
                # here we check the person sending is logged in and the recipient account has been created
                logged_in_lock.acquire()
                if (not (client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('SEND_MESSAGE_RESPONSE', id_accum, {
                                                                 'status': 'Error: Need to be logged in to send a message.'})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                else:
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (
                        client_socket, socket_lock)][0]
                    logged_in_lock.release()
                    recipient = args["recipient"]
                    message = args["message"]
                    account_list_lock.acquire()
                    if (not recipient in account_list):
                        account_list_lock.release()
                        response = protocol.protocol_instance.encode('SEND_MESSAGE_RESPONSE', id_accum, {
                                                                     'status': 'Error: The recipient of the message does not exist.'})
                        protocol.protocol_instance.send(
                            client_socket, response, socket_lock)
                    else:
                        undelivered_msg_lock.acquire()
                        if (recipient in undelivered_msg.keys()):
                            undelivered_msg[recipient] = undelivered_msg[recipient] + \
                                [(username, message)]
                        else:
                            undelivered_msg[recipient] = [(username, message)]
                        undelivered_msg_lock.release()
                        account_list_lock.release()  # ACCOUNT LIST > UNDELIVERED MSG

            case 7:  # DELETE
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (
                        client_socket, socket_lock)][0]
                    logged_in_user_to_client_socket.pop(username)
                    logged_in_lock.release()
                    account_list_lock.acquire()
                    account_list.remove(username)
                    account_list_lock.release()
                    response = protocol.protocol_instance.encode(
                        'DELETE_ACCOUNT_RESPONSE', id_accum, {'status': 'Success'})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                else:
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('DELETE_ACCOUNT_RESPONSE', id_accum, {
                                                                 'status': 'Error: Need to be logged in to delete your account.'})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
            case 9:  # LOGIN
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {
                                                                 'status': 'Error: Already logged into an account, please log off first.', 'username': ''})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                else:
                    account_name = args['username']
                    if (not atomicIsAccountCreated(account_name)):
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode(
                            'LOG_IN_RESPONSE', id_accum, {'status': 'Error: Account does not exist.', 'username': account_name})
                        protocol.protocol_instance.send(
                            client_socket, response, socket_lock)
                    elif (account_name in logged_in_user_to_client_socket.keys()):
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode('LOG_IN_RESPONSE', id_accum, {
                                                                     'status': 'Error: Someone else is logged into that account.', 'username': account_name})
                        protocol.protocol_instance.send(
                            client_socket, response, socket_lock)
                    else:
                        logged_in_user_to_client_socket[account_name] = (
                            client_socket, socket_lock)
                        logged_in_lock.release()
                        response = protocol.protocol_instance.encode(
                            'LOG_IN_RESPONSE', id_accum, {'status': 'Success', 'username': account_name})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
            case 11:  # LOGOFF
                logged_in_lock.acquire()
                if ((client_socket, socket_lock) in logged_in_user_to_client_socket.values()):
                    username = [k for k, v in logged_in_user_to_client_socket.items() if v == (
                        client_socket, socket_lock)][0]
                    logged_in_user_to_client_socket.pop(username)
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode(
                        'LOG_OFF_RESPONSE', id_accum, {'status': 'Success'})
                    protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
                else:
                    logged_in_lock.release()
                    response = protocol.protocol_instance.encode('LOG_OFF_RESPONSE', id_accum, {
                                                                 'status': 'Error: Need to be logged in to log out of your account.'})
                    protocol.protocol_instance.protocol.protocol_instance.send(
                        client_socket, response, socket_lock)
    return process_operation


def handle_undelivered_messages():
    undelivered_msg_lock.acquire()
    for (k, v) in undelivered_msg.items():
        logged_in_lock.acquire()
        if (k in logged_in_user_to_client_socket):
            (client_socket, socket_lock) = logged_in_user_to_client_socket(k)
            for (sender, msg) in v:
                response = protocol.protocol_instance.encode(
                    "RECV_MESSAGE", msg_accum, {"sender": k, "message": msg})
                protocol.protocol_instance.send(
                    client_socket, response, socket_lock)
        logged_in_lock.release()
    undelivered_msg_lock.release()
