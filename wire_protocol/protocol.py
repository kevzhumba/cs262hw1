from enum import Enum
from typing import Dict, List

METADATA_SIZES = {
    "version": 1,
    "header_length": 1,
    "operation_code": 1,
    "message_size": 3,
    "payload_size": 2,
    "message_id": 2,
}

METADATA_LENGTH = sum(METADATA_SIZES.values())
MAX_PAYLOAD_SIZE = 2048
VERSION = 1


class OperationCode(Enum):
    CREATE_ACCOUNT = 1
    CREATE_ACCOUNT_RESPONSE = 2
    LIST_ACCOUNTS = 3
    LIST_ACCOUNTS_RESPONSE = 4
    SEND_MESSAGE = 5
    SEND_MESSAGE_RESPONSE = 6
    DELETE_ACCOUNT = 7
    DELETE_ACCOUNT_RESPONSE = 8
    LOG_IN = 9
    LOG_IN_RESPONSE = 10
    LOG_OFF = 11
    LOG_OFF_RESPONSE = 12
    RECV_MESSAGE = 13


OPERATION_ARGS = {
    'CREATE_ACCOUNT': ['username'],
    'CREATE_ACCOUNT_RESPONSE': ['status'],
    'LIST_ACCOUNTS': ['query'],
    'LIST_ACCOUNTS_RESPONSE': ['status', 'accounts'],
    'SEND_MESSAGE': ['recipient', 'message'],
    'SEND_MESSAGE_RESPONSE': ['status'],
    'DELETE_ACCOUNT': [],
    'DELETE_ACCOUNT_RESPONSE': ['status'],
    'LOG_IN': ['username'],
    'LOG_IN_RESPONSE': ['status'],
    'LOG_OFF': [],
    'LOG_OFF_RESPONSE': ['status'],
    'RECV_MESSAGE': ['sender', 'message']
}


class Message:
    def __init__(self, version, operation, data):
        self.version = version
        self.operation = operation
        self.data = data

    def __str__(self):
        return f"Version: {self.version}, Operation: {self.operation}, Data: {self.data}"

    def get_version(self) -> int:
        return self.version


class Metadata:
    def __init__(self, version: bytes, header_length: bytes, operation_code: bytes,
                 message_size: bytes, payload_size: bytes, message_id: bytes) -> None:
        self.version = int.from_bytes(version, 'big')
        self.header_length = int.from_bytes(header_length, 'big')
        self.operation_code = OperationCode(
            int.from_bytes(operation_code, 'big'))
        self.message_size = int.from_bytes(message_size, 'big')
        self.payload_size = int.from_bytes(payload_size, 'big')
        self.message_id = int.from_bytes(message_id, 'big')


class Protocol:
    def __init__(self, version: int, metadata_sizes: Dict[str, int]) -> None:
        self.version = version
        self.metadata_sizes = metadata_sizes
        self.header_length = self._get_header_length()

        self.separator = '\r'

    def _get_header_length(self) -> int:
        return self.metadata_sizes['operation_code'] + \
            self.metadata_sizes['message_size'] + \
            self.metadata_sizes['payload_size'] + \
            self.metadata_sizes['message_id']

    def encode(self, operation: str, message_id: int, operation_args={}) -> List[bytes]:
        # Check for necessary arguments
        if set(OPERATION_ARGS[operation]).intersection(set(operation_args.keys())) != set(OPERATION_ARGS[operation]):
            raise ValueError(
                f"Missing arguments for operation {operation}. Required arguments: {OPERATION_ARGS[operation]}")

        # Join keyword arguments with separator
        data = self.separator.join(
            [f"{key}={value}" if key in OPERATION_ARGS[operation] else "" for key, value in operation_args.items()])

        # Encode metadata and data into byte messages (multiple for large messages)
        return self._encode(OperationCode[operation].value, message_id, data)

    def _encode(self, operation: int, message_id: int, data: str) -> List[bytes]:
        # Encode data
        encoded_data = self._encode_data(data)

        # Encode metadata
        bytes = bytearray(self._encode_component('version', self.version))
        bytes.extend(self._encode_component(
            'header_length', self.header_length))
        bytes.extend(self._encode_component('operation_code', operation))
        bytes.extend(self._encode_component('message_size', len(encoded_data)))

        encoded_payloads = []

        # Split into payloads of MAX_PAYLOAD_SIZE bytes, all with same common metadata
        for i in range(0, len(encoded_data), MAX_PAYLOAD_SIZE):
            payload = encoded_data[i:i+MAX_PAYLOAD_SIZE]
            payload_bytes = bytes + \
                self._encode_component('payload_size', len(payload))
            payload_bytes.extend(
                self._encode_component('message_id', message_id))
            payload_bytes.extend(payload)
            encoded_payloads.append(payload_bytes)

        return encoded_payloads

    def _encode_component(self, component: str, value: int) -> bytes:
        return value.to_bytes(self.metadata_sizes[component], byteorder='big')

    def _encode_data(self, data: str) -> bytes:
        return data.encode('ascii')

    def send(self, client_socket, msg, socket_lock=None):
        if socket_lock is not None:
            socket_lock.acquire()
        accum = 0
        targetSize = len(msg)
        while (not accum == targetSize):
            sent = client_socket.send(msg, MAX_PAYLOAD_SIZE)
            if (sent == 0):
                # TODO handle correctly
                socket_lock.release()
                raise RuntimeError("socket connection broken")
            accum += sent
        if socket_lock is not None:
            socket_lock.release()

    def parse_data(self, op: int, data: str) -> dict[str, str]:
        kv_pairs = data.split(
            self.separator, OPERATION_ARGS[OperationCode(op).name])
        dict(map(lambda x: tuple(x.split("=", 1)), kv_pairs))

    def parse_metadata(self, bytes) -> Metadata:
        '''
            Takes in a bytes object and parses the metadata. 
        '''
        # bytes is the result of client recv
        # idx is the byte index into the metadata we are currently readin
        return Metadata(bytes[0:1], bytes[1:2], bytes[2:3], bytes[3:6], bytes[6:8], bytes[8:10])

    def read_packets(self, client, processFn):
        # Handle ending/disconnecting later
        curr_msg_id = -1
        curr_op = -1
        msg_id_accum = 0
        # represents the bytes from the last recieve that occurred after packet termination; invariant has to be that left_over_packet ALWAYS starts with a header.
        left_over_packet = bytes()
        running_msg = ""
        while True:
            # chekc user input
            # if user input exists then send
            msg = client.recv(MAX_PAYLOAD_SIZE)
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
                    md = self.parse_metadata(curr_msg_to_parse)
                    if (not (md.version == VERSION)):
                        # TODO throw response error, also maybe make sure that no packets of the same message id are processed
                        return None
                    else:
                        curr_payload_size = md.payload_size
                        if (len(curr_msg_to_parse[METADATA_LENGTH:]) < curr_payload_size):
                            # wait to receive more since we dont have the entire payload yet
                            continue_iteration = False
                        else:
                            # now we have the whole packet, we can parse the data.
                            # parse payload size of the built up msg starting from after the metadata
                            packet_to_parse = curr_msg_to_parse[METADATA_LENGTH:
                                                                curr_payload_size + METADATA_LENGTH]
                            incomplete_msg = packet_to_parse.decode('ascii')
                            if (curr_msg_id == md.message_id and curr_op == md.operation_code):
                                running_msg += incomplete_msg
                            else:
                                # else this is a new message
                                running_msg = incomplete_msg
                                curr_msg_id = md.message_id
                            # if running msg is done, then do something based on op codes and such
                            if (running_msg[-1] == '\n'):
                                # TODO do something, reset running vars
                                processFn(client, md, running_msg,
                                          msg_id_accum)
                                msg_id_accum += 1
                                curr_msg_id = -1
                                curr_op = -1
                                running_msg = ''
                            # once we've processed the current packet, we want to set the curr_msg_to_parse
                            # to be the rest of the total msg, and then iterate over the total msg to parse again
                            curr_msg_to_parse = curr_msg_to_parse[curr_payload_size +
                                                                  METADATA_LENGTH:]
                left_over_packet = curr_msg_to_parse


protocol_instance = Protocol(VERSION, METADATA_SIZES)
