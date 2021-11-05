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

class WorkerConectados(QObject):
    finished = pyqtSignal()
    #progress = pyqtSignal(int)
    progress = pyqtSignal()
    switchPage = pyqtSignal(int)
    chooseAnotherNickname = pyqtSignal()
    updateConnectedUsers = pyqtSignal(str)
    addDesconectedUsers = pyqtSignal(str)
    deleteAllConnectedUsers = pyqtSignal()
    atualizarTimerConexao = pyqtSignal(int)
    
    global encerrar

    def run(self):
        global encerrar
        while encerrar == False:
            try:
                message = self.client.recv(1024).decode('utf-8')
                
                #message_tuple = tuple(map(str, message.split('||')))
                message_tuple = message.split(',')

                if(message_tuple[0]=='!conectado'):  print('[servidor conectado]')
                elif(message_tuple[0]=='!encerrar'):
                    encerrar = True
                    self.client.close()
                    print('[servidor desconectado]')
                    break
                elif(message_tuple[0]=='!removido'):
                    self.client.close()
                    print('[servidor desconectado - !removido]')
                    break
                elif(message_tuple[0] == '!mudar-tela'):
                    #self.view.switchPage(int(message_tuple[1]))
                    self.switchPage.emit(int(message_tuple[1]))
                # elif(message_tuple[0] == '!iniciar'):
                #     pass
                # elif(message_tuple[0] == '!iniciar-time-bar'):
                #     self.view.tela_conexao.timeBarControl()
                # elif(message_tuple[0] == '!definir-tema'):
                #     self.view.tela_jogo.definirTema()
                elif(message_tuple[0] == '!apelido-ja-existe'):
                    #self.view.tela_conexao.escolherOutroApelido()
                    self.chooseAnotherNickname.emit()
                elif(message_tuple[0] == "!Ap-conectados"):
                    aps = message_tuple[1].split('*')
                    textAps = ''
                    self.deleteAllConnectedUsers.emit()
                    for apelido in aps:
                        #textAps= textAps+'<span style=\"color: black;\">{} </span><span style=\"color: green;\">entrou </span><br>'.format(apelido)
                        textAps= '<span style=\"color: black;\">{} </span><span style=\"color: green;\">entrou </span>'.format(apelido)
                        #self.view.conectadosTemplate = textAps
                        self.updateConnectedUsers.emit(textAps)

                elif(message_tuple[0]=='!Ap-desconectado'):
                    ap = message_tuple[1]
                    textAp = '<span style=\"color: black;\">{} </span><span style=\"color: red;\">saiu </span>'.format(ap)
                    self.addDesconectedUsers.emit(textAp)
                elif(message_tuple[0]=='!print'):    print(message_tuple[1])
                elif(message_tuple[0]=='!atualizarTimerConexao'):
                    self.atualizarTimerConexao.emit(int(message_tuple[1]))
                elif(message_tuple[0]!=''): print("server: "+ str(message_tuple))

            except:
                print("An error occured!")
                self.client.close()
                break
        self.client.close()
        self.finished.emit()

        # while encerrar == False:
        #     time.sleep(1)
        #     self.progress.emit()
        #     #self.progress.emit(i)
        # self.finished.emit()
    
    def conectar(self, client):
        self.client = client

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
        self.caixa_conexao.setReadOnly(True)
        self.bloco3.addWidget(QLabel('Aguardando jogadores'))
        self.btn_iniciar = QPushButton('Iniciar Partida')
        self.btn_iniciar.clicked.connect(lambda: self.main.iniciarPartida())
        self.bloco3.addWidget(self.caixa_conexao)
        self.bloco3.addWidget(self.btn_iniciar)

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

    def setarApelidosConectados(self, msg):
        #self.caixa_conexao.setText(msg)
        self.caixa_conexao.append(msg)
    
    def adicionarApelidoDesconectado(self, msg):
        # text = self.caixa_conexao.toPlainText()
        # text = text+msg
        #self.caixa_conexao.insertHtml(msg)
        self.caixa_conexao.append(msg)

    def timeBarSetter(self, valor):
        self.time_bar.setValue(valor)
        self.time_bar.setFormat(f"{str(valor)} segundos") 
        self.time_bar.setAlignment(Qt.AlignCenter)

    def escolherOutroApelido(self):
        self.status_conexao.setText('<span style=\"color: orange;\">O apelido já existe!</span>')
        self.apelido_input.setEnabled(True)
        self.conectar_botao.setEnabled(True)
        self.main.desconectar()

    def apagarCaixaConexao(self):
        self.caixa_conexao.setText('')


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
                                        "background-color: #1320d3;"
                                    "}"
                                    )

        self.tempo.setFormat('') 
        self.bloco4.addWidget(self.tempo)
        self.tentativaRespostaInput = QLineEdit()
        self.tentativaRespostaInput.returnPressed.connect(lambda: self.enviarResposta())
        self.bloco4.addWidget(self.tentativaRespostaInput)

        self.divEsquerda.addLayout(self.bloco1)
        self.divDireita.addLayout(self.bloco2)
        self.divDireita.addLayout(self.bloco3)
        self.divDireita.addLayout(self.bloco4)

        self.layout.addLayout(self.divEsquerda)
        self.layout.addLayout(self.divDireita)


    def enviarResposta(self):
        resposta = self.tentativaRespostaInput.text()
        self.tentativaRespostaInput.setText('')
        self.main.client.send(f"!resposta,{resposta}".encode('utf-8'))

    def definirTema(self):
        dlg = QDialog()
        dlg.setGeometry(20, 80, 400, 500)
        dlgLayout = QVBoxLayout()
        dlg.setLayout(dlgLayout)
        dlg.setWindowTitle('Sua vez')

        blocoA = QVBoxLayout()
        blocoA.addWidget(QLabel('Tema'))
        temaInput = QLineEdit()
        blocoA.addWidget(temaInput)
        blocoA.addWidget(QLabel('Dica'))
        dicaInput = QLineEdit()
        blocoA.addWidget(dicaInput)
        blocoA.addWidget(QLabel('Resposta'))
        respostaInput = QLineEdit()
        respostaInput.setStyleSheet("QLineEdit"
                                    "{"
                                    "margin-bottom: 80px;"
                                    "}")
        blocoA.addWidget(respostaInput)

        blocoB = QVBoxLayout()
        iniciarRodadaBtn = QPushButton('Iniciar Rodada')
        blocoB.addWidget(iniciarRodadaBtn)
        timer = QProgressBar()
        timer.setValue(100)
        timer.setStyleSheet("QProgressBar"
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
        blocoB.addWidget(timer)

        dlgLayout.addLayout(blocoA)
        dlgLayout.addLayout(blocoB)

        dlg.exec_()

class Tela(QWidget):
    def __init__(self):
        super().__init__()
        self.montar()

        self.conectadosTemplate = '<span style=\"color: black;\">Alessandro </span><span style=\"color: green;\">entrou </span><br>'
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

        
        self.show()
    
    # def setarConectores(self, receptor):
    #     self.receptor = receptor

    def setarConectores(self, receptor):
        self.receptor = receptor

    def conectar(self):
        address = self.tela_conexao.servidor_input.text()
        separador = address.find(':')
        self.host = address[0:separador]
        self.port = address[(separador+1):]
        
        self.apelido = self.tela_conexao.apelido_input.text()
        print(f"[Tentando conectar: {address}]")
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.receptor = ThreadReceptor(self)
            self.client.connect((self.host, int(self.port)))
            #self.receptor.conectar(self.host, self.port, self.client)
            
            # self.receptor.start()
            self.mountReceiver()
            self.receiver.conectar(self.client)
            self.thread.start()
            self.tela_conexao.status_conexao.setText('<span style=\"color: green;\">Servidor conectado</span>')
            self.client.send(f"!definir-apelido,{self.apelido}".encode('utf-8'))
            self.tela_conexao.conectar_botao.setEnabled(False)
            self.tela_conexao.apelido_input.setEnabled(False)
            self.tela_conexao.servidor_input.setEnabled(False)
        except:
            print("[Exception]: Tela().conectar")
            self.tela_conexao.status_conexao.setText('<span style=\"color: red;\">Servidor não encontrado</span>')

    def desconectar(self):
        self.client.send("!sair".encode('utf-8'))

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

    def iniciarPartida(self):
        print("INICIANDO PARTIDA")
        self.client.send(f"!iniciar-partida".encode('utf-8'))

    def mountReceiver(self):
        self.thread = QThread() # Instanciando uma thread em paralelo à principal -> QAplication.exec
        self.receiver = WorkerConectados()  # Instanciando um "trabalhador" objeto para trabalhar em outra thread
        self.receiver.moveToThread(self.thread)   # Movendo o "trabalhador" para a nova thread
            # Connectado signals e slots
        self.thread.started.connect(self.receiver.run)
        self.receiver.finished.connect(self.thread.quit)
        #self.receiver.finished.connect(self.receiver.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.receiver.progress.connect(lambda: self.tela_conexao.setarApelidosConectados(self.conectadosTemplate))
        self.receiver.switchPage.connect(self.switchPage)
        self.receiver.chooseAnotherNickname.connect(self.tela_conexao.escolherOutroApelido)
        self.receiver.updateConnectedUsers.connect(self.tela_conexao.setarApelidosConectados)
        self.receiver.addDesconectedUsers.connect(self.tela_conexao.adicionarApelidoDesconectado)
        self.receiver.deleteAllConnectedUsers.connect(self.tela_conexao.apagarCaixaConexao)
        self.receiver.atualizarTimerConexao.connect(self.tela_conexao.timeBarSetter)




# class ThreadReceptor(threading.Thread):
#     def __init__(self, view):
#         super(ThreadReceptor, self).__init__()
#         self.view = view
#         self.kill = threading.Event()

#     def run(self):
#         global encerrar
#         while encerrar == False:
#             try:
#                 message = self.client.recv(1024).decode('utf-8')
                
#                 #message_tuple = tuple(map(str, message.split('||')))
#                 message_tuple = message.split(',')

#                 if(message_tuple[0]=='!conectado'):  print('[servidor conectado]')
#                 elif(message_tuple[0]=='!encerrar'):
#                     encerrar = True
#                     self.client.close()
#                     break
#                 elif(message_tuple[0]=='!removido'):
#                     self.client.close()
#                     break
#                 elif(message_tuple[0] == '!mudar-tela'):
#                     self.view.switchPage(int(message_tuple[1]))
#                 elif(message_tuple[0] == '!iniciar'):
#                     pass
#                 elif(message_tuple[0] == '!iniciar-time-bar'):
#                     self.view.tela_conexao.timeBarControl()
#                 elif(message_tuple[0] == '!definir-tema'):
#                     self.view.tela_jogo.definirTema()
#                 elif(message_tuple[0] == '!apelido-ja-existe'):
#                     print('[Apelido ja existe]')
#                     self.view.tela_conexao.escolherOutroApelido()
#                 elif(message_tuple[0] == "!Ap-conectados"):
#                     aps = message_tuple[1].split('-')
#                     textAps = ''
#                     for apelido in aps:
#                         textAps= textAps+'<span style=\"color: black;\">{} </span><span style=\"color: green;\">entrou </span><br>'.format(apelido)
#                         self.view.conectadosTemplate = textAps
#                 elif(message_tuple[0]=='!print'):    print(message_tuple[1])
#                 elif(message_tuple[0]!=''): print("server: "+ str(message_tuple))

#             except:
#                 print("An error occured!")
#                 self.client.close()
#                 break
#         self.client.close()

#     def conectar(self, host, port, client):
#         self.client = client

class gameController():
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = Tela()
        # self.receptor = ThreadReceptor(self.view)
        self.view.show()
        # self.view.setarConectores(self.receptor)
        self.iniciar()

    def iniciar(self):
        global encerrar
        encerrar = False
        self.app.exec()
        encerrar = True
        print("Saindo...")
        self.view.desconectar()


game = gameController()
