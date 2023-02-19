import client

if __name__ == '__main__':
    host = input('Enter host: ')
    port = int(input('Enter port: '))

    client_instance = client.Client(host, port)

    try:
        client_instance.connect()
        client_instance.run()
    except KeyboardInterrupt:
        client_instance.close()
        print('Disconnected from server')
