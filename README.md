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
- grpcio
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

