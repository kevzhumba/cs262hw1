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

MAX_PAYLOAD_SIZE = 2048


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
    'LIST_ACCOUNTS_RESPONSE': ['accounts'],
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
        self.operation_code = OperationCode(int.from_bytes(operation_code, 'big'))
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

    def encode(self, operation: str, message_id: int, **kwargs) -> List[bytes]:
        # Check for necessary arguments
        if set(OPERATION_ARGS[operation]).intersection(set(kwargs.keys())) != set(OPERATION_ARGS[operation]):
            raise ValueError(
                f"Missing arguments for operation {operation}. Required arguments: {OPERATION_ARGS[operation]}")

        # Join keyword arguments with separator
        data = self.separator.join(
            [f"{key}={value}" if key in OPERATION_ARGS[operation] else "" for key, value in kwargs.items()])

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

    def _decode(self, message: bytes) -> Message:
        #
        # Read in version number, make sure it matches global version
        # Read in header size, then parse in the next bits for the header size
        # Parse the header and its attributes
        # Read pa
        pass

    def parse_metadata(bytes) -> Metadata:
        '''
            Takes in a bytes object and parses the metadata. 
        '''
        # bytes is the result of client recv
        # idx is the byte index into the metadata we are currently readin
        return Metadata(bytes[0:1], bytes[1:2], bytes[2:3], bytes[3:6], bytes[6:8], bytes[8:10])
protocol_instance = Protocol(1, METADATA_SIZES)