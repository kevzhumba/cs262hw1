import socket
import protocol

HOST = '127.0.0.1'
PORT = 6000
METADATA_LENGTH = 10
VERSION = 1


def handle_client(client):
    # Handle ending/disconnecting later
    curr_msg_id = -1
    curr_payload_size = 0
    # represents the bytes from the last recieve that occurred after packet termination; invariant has to be that left_over_packet ALWAYS starts with a header.
    left_over_packet = bytes()
    last_recv_packet_termination = True
    running_msg = ""
    while True:
        msg = client.recv(1024)
        if (msg == 0):
            # client
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
                        left_over_packet = curr_msg_to_parse
                        continue_iteration = False
                    else:
                        # now we have the whole packet, we can parse the data.
                        # parse payload size of the built up msg starting from after the metadata
                        packet_to_parse = curr_msg_to_parse[10: curr_payload_size + 10]
                        incomplete_msg = packet_to_parse.decode('ascii')
                        if (curr_msg_id == md.message_id):
                            running_msg += incomplete_msg
                        else:
                            # else this is a new message
                            running_msg = incomplete_msg
                            curr_msg_id = md.message_id
                        # if running msg is done, then do something based on op codes and such
                        if (running_msg[-1] == '\n'):
                            # do something, set curr msg id to -1
                            curr_msg_id = -1
                            pass
                        # once we've processed the current packet, we want to set the curr_msg_to_parse
                        # to be the rest of the total msg, and then iterate over the total msg to parse again
                        if (len(curr_msg_to_parse) >= curr_payload_size + 10):
                            curr_msg_to_parse = curr_msg_to_parse[curr_payload_size+10:]
            left_over_packet = curr_msg_to_parse


def parse_metadata(bytes) -> protocol.Metadata:
    '''
        Takes in a bytes object and parses the metadata. 
    '''
    # bytes is the result of client recv
    # idx is the byte index into the metadata we are currently readin
    return protocol.Metadata(bytes[0:1], bytes[1:2], bytes[2:3], bytes[3:6], bytes[6:8], bytes[8:10])


def server_soc():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print("Server Started")
    clientsocket, addr = server_socket.accept()
    print('Connected to by:', addr)

    bdata = clientsocket.recv(128)
    data = bdata.decode('ascii')
