import socket
import threading
import sys
import time

host = '127.0.0.1'
port = 55555





class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.apelidos = []
        self.estaBloqueado = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.iniciar()


    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except:
                self.removerClient(client)

    def removerClient(self, client):
        try:
            index = self.clients.index(client)
            self.clients.remove(client)
            self.apelidos.remove(self.apelidos[index])
            client.close()
        except:
            pass

    def adicionarApelido(self, client, apelido):
        try:
            index = self.clients.index(client)
            self.apelidos.append(apelido)
            self.apelidos[index] = apelido
            self.broadcast(('!Ap-conectados,'+'-'.join(map(str, self.apelidos))).encode('utf-8'))
        except:
            print("[Except: adicionarApelido]")

    def escutar(self, client):
        while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    if(self.estaBloqueado==False):
                        #message_tuple = tuple(map(str, message.split('||')))
                        message_tuple = message.split(',')

                        if(message_tuple[0]=='!sair'):
                            client.send('!removido'.encode('utf-8'))
                            self.removerClient(client)
                            print('[Cliente desconectado]')
                            break
                        elif(message_tuple[0]=='!print'):
                            print('\n', message_tuple[1])
                        elif(message_tuple[0]=='!definir-apelido'):
                            print('[Apelido]')
                            if(message_tuple[1] in self.apelidos):
                                print('[Apelido já existe]')
                                time.sleep(0.005)
                                client.send('!apelido-ja-existe'.encode('utf-8'))
                                #removerClient(client)
                            else:
                                self.adicionarApelido(client, message_tuple[1])
                                print("cliente e apelido add: ", self.apelidos)

                        elif(message_tuple[0]!=''): print("cliente: "+ str(message_tuple))

                    
                except:
                    self.removerClient(client)
                    break



    # Receiving / Listening Function
    def entrada(self):
        global estaBloqueado
        while True:
            entrada = str(input('>: '))
            #entrada_tuple = tuple(map(str, entrada.split('||')))
            entrada_tuple = entrada.split(',')
            #removedorAspas = slice(1, -1)
            if(entrada_tuple[0]=='!bloquear'):
                self.estaBloqueado = True
            elif(entrada_tuple[0]=='!desbloquear'):
                self.estaBloqueado = False
            elif(entrada_tuple[0] == '*print-clients'): print("\n-- ", self.clients)
            elif(entrada_tuple[0] == '*print-apelidos'): print("\n-- ", self.apelidos, len(self.apelidos))
            else:   self.broadcast(str(entrada).encode('utf-8'))

    def iniciar(self):
        self.server.bind((self.host, int(self.port)))
        self.server.listen()
        self.threadEnviar = threading.Thread(target=self.entrada, args=())
        self.threadEnviar.start()
        while True:
            client, address = self.server.accept()
            if(self.estaBloqueado==False):
                print("Conectado com {}".format(str(address)))

                self.clients.append(client)

                client.send('!conectado'.encode('utf-8'))
                time.sleep(0.01)

                threadEscuta = threading.Thread(target=self.escutar, args=(client,))
                
                threadEscuta.start()



if len(sys.argv) != 3:
    print("use:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1:3]
server = Server(host, port)