import socket
import threading

host = '127.0.0.1'
port = 55555
estaBloqueado = False


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def removerClient(client):
        index = clients.index(client)
        clients.remove(client)
        client.close()

def escutar(client):
    while True:
            try:
                message = client.recv(1024).decode('ascii')
                if(estaBloqueado==False):
                    message_tuple = tuple(map(str, message.split('||')))

                    if(message_tuple[0]=='SAIR'):
                        removerClient(client)
                        print('\nClient desconected')
                        break
                    elif(message_tuple[0]=='PRINT'):
                        print('\n', message_tuple[1])
                    else:
                        print('client: '+ str(message_tuple))

                
            except:
                removerClient(client)
                break


# Receiving / Listening Function
def entrada(client):
    global estaBloqueado
    while True:
        entrada = str(input('>: '))
        entrada_tuple = tuple(map(str, entrada.split('||')))
        #removedorAspas = slice(1, -1)
        if(entrada_tuple[0]=='BLOQUEAR'):
            estaBloqueado = True
        elif(entrada_tuple[0]=='DESBLOQUEAR'):
            estaBloqueado = False
        else:   broadcast(str(entrada).encode('ascii'))

def iniciar():
    while True:
        client, address = server.accept()
        if(estaBloqueado==False):
            print("Conectado com {}".format(str(address)))

            clients.append(client)

            client.send('CONECTADO'.encode('utf-8'))

            threadEscuta = threading.Thread(target=escutar, args=(client,))
            threadEnviar = threading.Thread(target=entrada, args=(client,))
            threadEscuta.start()
            threadEnviar.start()


iniciar()