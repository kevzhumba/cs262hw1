import client

if __name__ == '__main__':
    client_instance = client.Client()

    host = input('Enter host: ')
    port = int(input('Enter port: '))

    try:
        client_instance.connect(host, port)
        client_instance.run()
    except KeyboardInterrupt:
        client_instance.close()
        print('Disconnected from server')
