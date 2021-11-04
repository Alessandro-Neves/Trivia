import socket
import threading
import sys
import time

host = '127.0.0.1'
port = 55555
estaBloqueado = False


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


clients = []
apelidos = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            removerClient(client)

def removerClient(client):
    try:
        index = clients.index(client)
        clients.remove(client)
        client.close()
    except:
        pass

def escutar(client):
    while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if(estaBloqueado==False):
                    message_tuple = tuple(map(str, message.split('||')))

                    if(message_tuple[0]=='!sair'):
                        client.send('!removido'.encode('utf-8'))
                        removerClient(client)
                        print('[Cliente desconectado]')
                        break
                    elif(message_tuple[0]=='!print'):
                        print('\n', message_tuple[1])
                    elif(message_tuple[0]=='!definir-apelido'):
                        print('[Apelido]')
                        if(message_tuple[1]=='Alessandro'):
                            print('[Apelido já existe]')
                            time.sleep(0.01)
                            client.send('!apelido-ja-existe'.encode('utf-8'))
                            #removerClient(client)
                        else: print("cliente: "+ str(message_tuple))

                    elif(message_tuple[0]!=''): print("cliente: "+ str(message_tuple))

                
            except:
                removerClient(client)
                break


# Receiving / Listening Function
def entrada():
    global estaBloqueado
    while True:
        entrada = str(input('>: '))
        entrada_tuple = tuple(map(str, entrada.split('||')))
        #removedorAspas = slice(1, -1)
        if(entrada_tuple[0]=='!bloquear'):
            estaBloqueado = True
        elif(entrada_tuple[0]=='!desbloquear'):
            estaBloqueado = False
        elif(entrada_tuple[0] == '*print-clients'): print("\n-- ", clients)
        else:   broadcast(str(entrada).encode('utf-8'))

def iniciar():
    server.bind((host, int(port)))
    server.listen()
    threadEnviar = threading.Thread(target=entrada, args=())
    threadEnviar.start()
    while True:
        client, address = server.accept()
        if(estaBloqueado==False):
            print("Conectado com {}".format(str(address)))

            clients.append(client)

            client.send('!conectado'.encode('utf-8'))

            threadEscuta = threading.Thread(target=escutar, args=(client,))
            
            threadEscuta.start()



if len(sys.argv) != 3:
    print("use:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1:3]
iniciar()