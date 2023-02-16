import client

if __name__ == '__main__':
    client_instance = client.Client()
    
    host = input('Enter host: ')
    port = int(input('Enter port: '))
    
    client_instance.connect(host, port)
    client_instance.run()
    
    client_instance.close()