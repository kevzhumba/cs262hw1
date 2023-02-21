# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_service_pb2 as chat__service__pb2


class ChatServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateAccount = channel.unary_unary(
                '/chatservice.ChatService/CreateAccount',
                request_serializer=chat__service__pb2.CreateAccountRequest.SerializeToString,
                response_deserializer=chat__service__pb2.CreateAccountResponse.FromString,
                )
        self.ListAccounts = channel.unary_unary(
                '/chatservice.ChatService/ListAccounts',
                request_serializer=chat__service__pb2.ListAccountsRequest.SerializeToString,
                response_deserializer=chat__service__pb2.ListAccountsResponse.FromString,
                )
        self.SendMessage = channel.unary_unary(
                '/chatservice.ChatService/SendMessage',
                request_serializer=chat__service__pb2.SendMessageRequest.SerializeToString,
                response_deserializer=chat__service__pb2.SendMessageResponse.FromString,
                )
        self.DeleteAccount = channel.unary_unary(
                '/chatservice.ChatService/DeleteAccount',
                request_serializer=chat__service__pb2.DeleteAccountRequest.SerializeToString,
                response_deserializer=chat__service__pb2.DeleteAccountResponse.FromString,
                )
        self.LogIn = channel.unary_unary(
                '/chatservice.ChatService/LogIn',
                request_serializer=chat__service__pb2.LogInRequest.SerializeToString,
                response_deserializer=chat__service__pb2.LogInResponse.FromString,
                )
        self.LogOff = channel.unary_unary(
                '/chatservice.ChatService/LogOff',
                request_serializer=chat__service__pb2.LogOffRequest.SerializeToString,
                response_deserializer=chat__service__pb2.LogOffResponse.FromString,
                )
        self.GetMessages = channel.unary_stream(
                '/chatservice.ChatService/GetMessages',
                request_serializer=chat__service__pb2.GetMessagesRequest.SerializeToString,
                response_deserializer=chat__service__pb2.ChatMessage.FromString,
                )


class ChatServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListAccounts(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LogIn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LogOff(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMessages(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateAccount,
                    request_deserializer=chat__service__pb2.CreateAccountRequest.FromString,
                    response_serializer=chat__service__pb2.CreateAccountResponse.SerializeToString,
            ),
            'ListAccounts': grpc.unary_unary_rpc_method_handler(
                    servicer.ListAccounts,
                    request_deserializer=chat__service__pb2.ListAccountsRequest.FromString,
                    response_serializer=chat__service__pb2.ListAccountsResponse.SerializeToString,
            ),
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=chat__service__pb2.SendMessageRequest.FromString,
                    response_serializer=chat__service__pb2.SendMessageResponse.SerializeToString,
            ),
            'DeleteAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAccount,
                    request_deserializer=chat__service__pb2.DeleteAccountRequest.FromString,
                    response_serializer=chat__service__pb2.DeleteAccountResponse.SerializeToString,
            ),
            'LogIn': grpc.unary_unary_rpc_method_handler(
                    servicer.LogIn,
                    request_deserializer=chat__service__pb2.LogInRequest.FromString,
                    response_serializer=chat__service__pb2.LogInResponse.SerializeToString,
            ),
            'LogOff': grpc.unary_unary_rpc_method_handler(
                    servicer.LogOff,
                    request_deserializer=chat__service__pb2.LogOffRequest.FromString,
                    response_serializer=chat__service__pb2.LogOffResponse.SerializeToString,
            ),
            'GetMessages': grpc.unary_stream_rpc_method_handler(
                    servicer.GetMessages,
                    request_deserializer=chat__service__pb2.GetMessagesRequest.FromString,
                    response_serializer=chat__service__pb2.ChatMessage.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chatservice.ChatService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/CreateAccount',
            chat__service__pb2.CreateAccountRequest.SerializeToString,
            chat__service__pb2.CreateAccountResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListAccounts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/ListAccounts',
            chat__service__pb2.ListAccountsRequest.SerializeToString,
            chat__service__pb2.ListAccountsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/SendMessage',
            chat__service__pb2.SendMessageRequest.SerializeToString,
            chat__service__pb2.SendMessageResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/DeleteAccount',
            chat__service__pb2.DeleteAccountRequest.SerializeToString,
            chat__service__pb2.DeleteAccountResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def LogIn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/LogIn',
            chat__service__pb2.LogInRequest.SerializeToString,
            chat__service__pb2.LogInResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def LogOff(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatService/LogOff',
            chat__service__pb2.LogOffRequest.SerializeToString,
            chat__service__pb2.LogOffResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatservice.ChatService/GetMessages',
            chat__service__pb2.GetMessagesRequest.SerializeToString,
            chat__service__pb2.ChatMessage.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
