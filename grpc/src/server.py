from concurrent import futures
import logging
import math
import time

import grpc
import chat_service_pb2
import chat_service_pb2_grpc


class ChatServiceServicer(chat_service_pb2_grpc.ChatServiceServicer):
