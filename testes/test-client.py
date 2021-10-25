import socket
import threading
import sys
import time


# Choosing Nickname
#nickname = input("Choose your nickname: ")

## Encapsulando Thread
class ThreadReceiver(threading.Thread):

    def __init__(self, client):
        super(ThreadReceiver, self).__init__()
        self.kill = threading.Event()
        self.client = client

    def run(self):
        # Enquanto a thread não estiver 'morta'
        while True:
            try:
                # If 'NICK' Send Nickname
                message = self.client.recv(1024).decode('utf-8')
                # if message == 'NICK':
                #     self.client.send(nickname.encode('ascii'))
                # elif message == 'EXIT':
                #     break
                # else:
                #     print(message)
                message_tuple = tuple(map(str, message.split('||'))) 
                

                if(message_tuple[0]=='CONECTADO'):  print('Servidor encontrado e conectado')
                elif(message_tuple[0]=='SAIR'):
                    print('SAINDO...')
                    self.client.close()
                    break
                elif(message_tuple[0]=='PRINT'):    print(message_tuple[1])
                else: print("server: "+ str(message_tuple))

            except:
                # Close Connection When Error
                print("An error occured!")
                self.client.close()
                break

    def stop(self):
        # Mata a thread
        print("thread parando.")
        self.kill.set()


class ThreadWriter(threading.Thread):

    def __init__(self, client):
        super(ThreadWriter, self).__init__()
        self.kill = threading.Event()
        self.client = client

    def run(self):
        # Enquanto a thread não estiver 'morta'
        while True:
            message = str(input('> '))
            # if message == '{}: {}'.format(nickname, '\exit'):
            #     self.client.send(message.encode('ascii'))
            #     break
            self.client.send(message.encode('utf-8'))

    def stop(self):
        # Mata a thread
        print("thread parando.")
        self.kill.set()


class Conexao():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('127.0.0.1', 55555))
            print('Conectado')
            self.start_socket()

        except:
            print('Não conectado')
    
    def stopall(self):
        print("Saindo!")
        time.sleep(5)
        self.receive_thread.stop()
        self.write_thread.stop()
        print("Encerrado")
        sys.exit()

    def start_socket(self):
        receive_thread = ThreadReceiver(self.client)
        receive_thread.start()

        write_thread = ThreadWriter(self.client)
        write_thread.start()

conexao = Conexao()