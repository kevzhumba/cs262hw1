import grpc
import chat_service_pb2
import chat_service_pb2_grpc

HOST = '127.0.0.1'
PORT = 6000


def run():
    with grpc.insecure_channel(f'{HOST}:{PORT}') as channel:
        stub = chat_service_pb2_grpc.ChatServiceStub(channel)
        response = stub.CreateAccount(
            chat_service_pb2.CreateAccountRequest(username="test"))
        print("CreateAccount client received: ", response)


if __name__ == '__main__':
    run()
