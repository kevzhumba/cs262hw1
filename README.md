# Design Exercise 1

## Overview
This is a simple chat messaging service. It supports multiple clients connecting to the server. We support several operations:
- Creating an account
- Logging into an existing account
- List exist accounts
- Sending a message to another user
- Logging out of an existing account
- Deleting an account
This functionality is implemented using both our own wire protocol, as well as using GRPC. The respective clients and servers can be found in the respective folders.

## Prerequisites
- MacOS
- Python 3.10
  - To upgrade using brew
    ```sh
    brew install python
    ```
  - To upgrade using conda (creates new environment)
    ```
    conda create -n py39 python=3.9 anaconda
    ```
- gRPCio
  
- google-api-python-client

## Setting up the Custom Wire Protocol Server
To run the server, first ensure that the machine that will be running the server has turned off their firewall. Then, from the project root, run 
```sh
python3 wire_protocol/run_server.py
```
If ```Server started``` is printed, then the server is ready to accept connections. To find the IP address which the server is being hosted at, go to 
```System Preferences -> Network -> Advanced -> TCP/IP```. The IP address the server is being hosted at should be listed there. The port for the server is 6000.

## Setting up the Custom Wire Protocol Client
To run the client, first ensure that the machine that will be running the server has turned off their firewall. Then, from the project root, run 
```sh
python3 wire_protocol/run_client.py
```
You will then be asked to input a hostname and port; the hostname can be found by following the above instructions on the server machine, and the port is 6000. If the connection is successful, you will see ```Connected to Server```. If not, check that the host and port are correct. 

## Sending Messages
The client will prompt for a command. Typing ```help``` will provide the user with various operations.
- 1: Create account 
- 2: Login 
- 3: List accounts 
- 4: Send message 
- 5: Logoff 
- 6: Delete account

Typing the number of a command will prompt the user for more information to fulfill the operation's request. 

## Client Error Messages
As you're sending messages, you might come across various errors. Each operation has several errors it can throw:
- Create account
  - If the account exists, the server will respond with an error
  - If the user is already logged in, the server will respond with an error
- Login 
  - If the user is already logged in, the server will respond with an error
  - If the supplied account is already logged into by another user, the server will respond with an error
  - If the supplied account doesn't exist, the server will respond with an error
- List accounts 
  - If the regex is malformed, the server will respond with an error
- Send message 
  - If the user is not logged in, the server will respond with an error
  - If the intended recipient of the message does not exist, the 
- Logoff 
  - If the user is not logged in, the server will respond with an error
- Delete account
  - If the user is not logged in, the server will respond with an error

## Stopping the Client/Server
To stop the client or server, simply press ```ctrl-C``` to exit the client or server.


