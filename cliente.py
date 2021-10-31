import socket
import threading
import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import (
    QApplication,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QWidget,
    QPushButton,
    QLabel,
    QTextEdit,
    QProgressBar,
    QDialog
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal

encerrar = False
port = ''
host = ''

class WorkerTimeBarControl(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        print("\t[WorkerTimeBarControl.run()]")
        for i in range(100, -1, -1):
            time.sleep(0.3)
            self.progress.emit(i)
        self.finished.emit() #à definir: função a ser chamada após o fim do tempo -> inicioDoJogo ou Restart

class TelaInicial(QWidget):
    def __init__(self, main):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.main = main
        self.bloco1 = QVBoxLayout()
        self.start_button = QPushButton('Começar')
        self.bloco1.setAlignment(Qt.AlignCenter) 
        self.start_button.clicked.connect(self.main.iniciar)
        self.bloco1.addWidget(self.start_button)
        self.layout.addLayout(self.bloco1)

        #estilos
        self.start_button.setStyleSheet("QPushButton ""{"
                                            "background-color: #2faa16;"
                                            "color: #ffffff;"
                                            "height: 80px;"
                                            "width: 300px;"
                                            "border-radius: 20px;"
                                            "font-size: 30px;"
                                            
                                        "}")



class TelaConexao(QWidget):
    def __init__(self, main):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        #Bloco 1
        self.main = main
        self.bloco1 = QVBoxLayout()
        #Componentes bloco 1
        self.apelido_input = QLineEdit()
        self.servidor_input = QLineEdit()
        self.bloco1.addWidget(QLabel('Apelido'))
        self.bloco1.addWidget(self.apelido_input)
        self.bloco1.addWidget(QLabel('Servidor (IP)'))
        self.bloco1.addWidget(self.servidor_input)
        
        #Bloco 2
        self.bloco2 = QHBoxLayout()
        #Componentes bloco 2
        self.conectar_botao = QPushButton('Conectar')
        self.conectar_botao.clicked.connect(lambda: self.main.conectar())
        self.status_conexao = QLabel('Servidor não conectado')
        self.status_conexao.setText('<span style=\"color: gray;\">Servidor não conectado</span>')
        self.status_conexao.setAlignment(QtCore.Qt.AlignCenter)
        self.bloco2.addWidget(self.conectar_botao)
        self.bloco2.addWidget(self.status_conexao)

        self.conectar_botao.setStyleSheet("QPushButton ""{""background-color: #1320d3;""}")

        #Bloco 3"
        self.bloco3 = QVBoxLayout()
        #Componentes bloco 3
        self.caixa_conexao = QTextEdit()
        self.bloco3.addWidget(QLabel('Aguardando jogadores'))
        self.bloco3.addWidget(self.caixa_conexao)

        #Bloco4
        self.bloco4 = QVBoxLayout()
        self.time_bar = QProgressBar()
        self.time_bar.setValue(100)
        self.time_bar.setStyleSheet("QProgressBar"
                                    "{"
                                        "color: #ffffff;"
                                        "text-align: center;"
                                        "background-color: #b2b2b6;"
                                        #"heigth: 40px;"
                                    "}"
                                    "QProgressBar::chunk"
                                    "{"
                                        "background-color: #1320d3"
                                    "}"
                                    )

        self.time_bar.setFormat('') 
        self.bloco4.addWidget(self.time_bar)

        #Adicionando bloco à tela
        self.layout.addLayout(self.bloco1)
        self.layout.addLayout(self.bloco2)
        self.layout.addLayout(self.bloco3)
        self.layout.addLayout(self.bloco4)


#[PASSAR CONTROLE PARA O SERVIDOR]
    def timeBarControl(self):
        self.thread = QThread() # Instanciando uma thread em paralelo à principal -> QAplication.exec
        self.worker = WorkerTimeBarControl()  # Instanciando um "trabalhador" objeto para trabalhar em outra thread
        self.worker.moveToThread(self.thread)   # Movendo o "trabalhador" para a nova thread
            # Connectado signals e slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.timeBarSetter)
        
        self.thread.start()


    def timeBarSetter(self, valor):
        self.time_bar.setValue(valor)
        self.time_bar.setFormat(f"{str(valor)} segundos") 
        self.time_bar.setAlignment(Qt.AlignCenter) 

class TelaJogo(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self.divEsquerda = QVBoxLayout()
        self.divDireita = QVBoxLayout()

        self.bloco1 = QVBoxLayout()
        self.bloco1.addWidget(QLabel('Jogadores'))
        self.caixaJogadores = QTextEdit()
        self.bloco1.addWidget(self.caixaJogadores)

        self.bloco2 = QVBoxLayout()
        self.dicaLabel = QLabel('Texto com x letras')
        self.pistaCaixa = QTextEdit()
        self.bloco2.addWidget(self.dicaLabel)
        self.bloco2.addWidget(self.pistaCaixa)

        self.bloco3 = QVBoxLayout()
        self.bloco3.addWidget(QLabel("Log"))
        self.caixaResposta = QTextEdit()
        self.bloco3.addWidget(self.caixaResposta)

        self.bloco4 = QVBoxLayout()
        self.tempo = QProgressBar()
        self.tempo.setValue(100)
        self.tempo.setStyleSheet("QProgressBar"
                                    "{"
                                        "color: #ffffff;"
                                        "text-align: center;"
                                        "background-color: #b2b2b6;"
                                        #"heigth: 40px;"
                                    "}"
                                    "QProgressBar::chunk"
                                    "{"
                                        "background-color: #1320d3"
                                    "}"
                                    )

        self.tempo.setFormat('') 
        self.bloco4.addWidget(self.tempo)
        self.tentativaRespostaInput = QLineEdit()
        self.bloco4.addWidget(self.tentativaRespostaInput)

        self.divEsquerda.addLayout(self.bloco1)
        self.divDireita.addLayout(self.bloco2)
        self.divDireita.addLayout(self.bloco3)
        self.divDireita.addLayout(self.bloco4)

        self.layout.addLayout(self.divEsquerda)
        self.layout.addLayout(self.divDireita)

class Tela(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trivia Game !")
        self.tela_inicial_index = 0
        self.tela_conexao_index = 1
        self.tela_jogo_index = 2
        self.tela_mestre_index = 3
        self.tela_podio = 4
        #enqudramento janela
        self.left = 20
        self.top = 80
        self.width = 400
        self.height = 500
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.montar()
        self.show()
    
    def setarConectores(self, transmissor, receptor):
        self.transmissor = transmissor
        self.receptor = receptor

    def conectar(self):
        # mudar para host port da tela
        global host
        global port
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, int(port)))
            self.transmissor.conectar(host, port, self.client)
            self.receptor.conectar(host, port, self.client)
            self.transmissor.start()
            self.receptor.start()
        except:
            print("[Exception]: Tela().conectar")

    def montar(self):
        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)

        self.tela_inicial = TelaInicial(self)
        self.tela_conexao = TelaConexao(self)
        self.tela_jogo = TelaJogo(self)

        self.stackedLayout.addWidget(self.tela_inicial)
        self.stackedLayout.addWidget(self.tela_conexao)
        self.stackedLayout.addWidget(self.tela_jogo)
        
    def iniciar(self):
        #startar controlador geral
        self.switchPage(self.tela_conexao_index)

    def switchPage(self, page_index):
        self.stackedLayout.setCurrentIndex(page_index)






class ThreadReceptor(threading.Thread):
    def __init__(self, view):
        super(ThreadReceptor, self).__init__()
        self.view = view
        self.kill = threading.Event()

    def run(self):
        global encerrar
        while encerrar == False:
            try:
                message = self.client.recv(1024).decode('utf-8')
                
                message_tuple = tuple(map(str, message.split('||'))) 

                if(message_tuple[0]=='!conectado'):  print('[servidor conectado]')
                elif(message_tuple[0]=='!sair'):
                    encerrar = True
                    self.client.close()
                    break
                elif(message_tuple[0] == '!mudar-tela'):
                    self.view.switchPage(int(message_tuple[1]))
                elif(message_tuple[0] == '!iniciar'):
                    pass
                elif(message_tuple[0] == '!iniciar-time-bar'):
                    self.view.tela_conexao.timeBarControl()
                elif(message_tuple[0]=='!print'):    print(message_tuple[1])
                elif(message_tuple[0]!=''): print("server: "+ str(message_tuple))

            except:
                print("An error occured!")
                self.client.close()
                break

    def conectar(self, host, port, client):
        self.client = client


class ThreadTransmissor(threading.Thread):

    def __init__(self):
        super(ThreadTransmissor, self).__init__()
        self.kill = threading.Event()

    def run(self):
        global encerrar
        while encerrar == False:
            message = str(input('> '))
            message_tuple = tuple(map(str, message.split('||'))) 
            
            if(message_tuple[0]=='!sair'):
                encerrar = True
                self.client.close()
                break
            self.client.send(message.encode('utf-8'))

    def conectar(self, host, port, client):
        self.client = client
        

    def stop(self):
        print("thread  transmissor parando.")
        self.kill.set()

class gameController():
    
    def __init__(self, host, port):
        
        self.host = host
        self.port = port

        self.app = QApplication(sys.argv)
        self.transmissor = ThreadTransmissor()
        self.view = Tela()
        self.receptor = ThreadReceptor(self.view)
        self.view.show()
        self.view.setarConectores(self.transmissor, self.receptor)
        self.iniciar()

    def test(self):
        global host
        global port
        host = self.host
        port = self.port
        # self.receptor.conectar(self.host, self.port)
        # self.transmissor.conectar(self.host, self.port)

    def iniciar(self):
        global encerrar
        self.test()
        # self.receptor.start()
        # self.transmissor.start()
        encerrar = False
        self.app.exec()



if len(sys.argv) != 3:
    print("use:", sys.argv[0], "<host> <port>")
    sys.exit(1)
host, port = sys.argv[1:3]
game = gameController(host, port)
