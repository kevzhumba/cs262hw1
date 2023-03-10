# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x63hat_service.proto\x12\x0b\x63hatservice\"(\n\x14\x43reateAccountRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"9\n\x15\x43reateAccountResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\"$\n\x13ListAccountsRequest\x12\r\n\x05query\x18\x01 \x01(\t\"8\n\x14ListAccountsResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63\x63ounts\x18\x02 \x03(\t\"8\n\x12SendMessageRequest\x12\x11\n\trecipient\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"%\n\x13SendMessageResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"\x16\n\x14\x44\x65leteAccountRequest\"\'\n\x15\x44\x65leteAccountResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\" \n\x0cLogInRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"1\n\rLogInResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\"\x0f\n\rLogOffRequest\" \n\x0eLogOffResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"\x14\n\x12GetMessagesRequest\".\n\x0b\x43hatMessage\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t2\xc1\x04\n\x0b\x43hatService\x12X\n\rCreateAccount\x12!.chatservice.CreateAccountRequest\x1a\".chatservice.CreateAccountResponse\"\x00\x12U\n\x0cListAccounts\x12 .chatservice.ListAccountsRequest\x1a!.chatservice.ListAccountsResponse\"\x00\x12R\n\x0bSendMessage\x12\x1f.chatservice.SendMessageRequest\x1a .chatservice.SendMessageResponse\"\x00\x12X\n\rDeleteAccount\x12!.chatservice.DeleteAccountRequest\x1a\".chatservice.DeleteAccountResponse\"\x00\x12@\n\x05LogIn\x12\x19.chatservice.LogInRequest\x1a\x1a.chatservice.LogInResponse\"\x00\x12\x43\n\x06LogOff\x12\x1a.chatservice.LogOffRequest\x1a\x1b.chatservice.LogOffResponse\"\x00\x12L\n\x0bGetMessages\x12\x1f.chatservice.GetMessagesRequest\x1a\x18.chatservice.ChatMessage\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CREATEACCOUNTREQUEST._serialized_start=35
  _CREATEACCOUNTREQUEST._serialized_end=75
  _CREATEACCOUNTRESPONSE._serialized_start=77
  _CREATEACCOUNTRESPONSE._serialized_end=134
  _LISTACCOUNTSREQUEST._serialized_start=136
  _LISTACCOUNTSREQUEST._serialized_end=172
  _LISTACCOUNTSRESPONSE._serialized_start=174
  _LISTACCOUNTSRESPONSE._serialized_end=230
  _SENDMESSAGEREQUEST._serialized_start=232
  _SENDMESSAGEREQUEST._serialized_end=288
  _SENDMESSAGERESPONSE._serialized_start=290
  _SENDMESSAGERESPONSE._serialized_end=327
  _DELETEACCOUNTREQUEST._serialized_start=329
  _DELETEACCOUNTREQUEST._serialized_end=351
  _DELETEACCOUNTRESPONSE._serialized_start=353
  _DELETEACCOUNTRESPONSE._serialized_end=392
  _LOGINREQUEST._serialized_start=394
  _LOGINREQUEST._serialized_end=426
  _LOGINRESPONSE._serialized_start=428
  _LOGINRESPONSE._serialized_end=477
  _LOGOFFREQUEST._serialized_start=479
  _LOGOFFREQUEST._serialized_end=494
  _LOGOFFRESPONSE._serialized_start=496
  _LOGOFFRESPONSE._serialized_end=528
  _GETMESSAGESREQUEST._serialized_start=530
  _GETMESSAGESREQUEST._serialized_end=550
  _CHATMESSAGE._serialized_start=552
  _CHATMESSAGE._serialized_end=598
  _CHATSERVICE._serialized_start=601
  _CHATSERVICE._serialized_end=1178
# @@protoc_insertion_point(module_scope)
