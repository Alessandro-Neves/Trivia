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

class Receptor(QObject):
    finished = pyqtSignal()
    #progress = pyqtSignal(int)
    progress = pyqtSignal()
    switchPage = pyqtSignal(int)
    chooseAnotherNickname = pyqtSignal()
    updateConnectedUsers = pyqtSignal(str)
    addDesconectedUsers = pyqtSignal(str)
    deleteAllConnectedUsers = pyqtSignal()
    atualizarTimerConexao = pyqtSignal(int, int)
    printLog = pyqtSignal(str, str)
    definirTema = pyqtSignal(str)
    
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
                elif(message_tuple[0] == '!iniciar-partida'):
                    self.switchPage.emit(2)
                elif(message_tuple[0] == '!definir-tema'):
                    self.definirTema.emit(message_tuple[1])
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
                    self.atualizarTimerConexao.emit(int(message_tuple[1]), int(message_tuple[2]))
                elif(message_tuple[0]=='!print-log'):
                    print("[receiver - print-log]\n")
                    print(message_tuple)
                    self.printLog.emit(message_tuple[1], message_tuple[2])

                else: print("server: "+ str(message_tuple))

            except:
                print("[Exception: WokerConectados - receiver]")
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
        self.apelido_input.setStyleSheet("QLineEdit"
                                    "{"
                                        "color: #1320d3;"
                                        "background-color: #ffffff;"
                                    "}")

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

        self.conectar_botao.setStyleSheet("QPushButton "
                                                "{"
                                                    "background-color: #1320d3;"
                                                    "color: #ffffff;"
                                                "}")

        #Bloco 3"
        self.bloco3 = QVBoxLayout()
        #Componentes bloco 3
        self.caixa_conexao = QTextEdit()
        self.caixa_conexao.setReadOnly(True)
        self.bloco3.addWidget(QLabel('Aguardando jogadores'))
        self.btn_iniciar = QPushButton('Iniciar Partida')
        self.btn_iniciar.setStyleSheet("QPushButton ""{"
                                            "background-color: green;"
                                            "color: #ffffff;"
                                        "}")
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

        #self.setStyleSheet("background-color: #ffffff;")

    def setarApelidosConectados(self, msg):
        #self.caixa_conexao.setText(msg)
        self.caixa_conexao.append(msg)
    
    def adicionarApelidoDesconectado(self, msg):
        # text = self.caixa_conexao.toPlainText()
        # text = text+msg
        #self.caixa_conexao.insertHtml(msg)
        self.caixa_conexao.append(msg)

    def timeBarSetter(self, valor, seconds):
        self.btn_iniciar.setEnabled(False)
        self.time_bar.setValue(valor)
        self.time_bar.setFormat(f"{str(seconds)} segundos") 
        self.time_bar.setAlignment(Qt.AlignCenter)

    def escolherOutroApelido(self):
        self.status_conexao.setText('<span style=\"color: orange;\">O apelido já existe!</span>')
        self.apelido_input.setEnabled(True)
        self.conectar_botao.setEnabled(True)
        self.main.desconectar()

    def apagarCaixaConexao(self):
        self.caixa_conexao.setText('')


class TelaDicaEspera(QWidget):
    def __init__(self, main):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.main = main
        self.bloco1 = QVBoxLayout()
        self.label = QLabel('Definindo tema ...')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.bloco1.setAlignment(Qt.AlignCenter) 
        #self.start_button.clicked.connect(self.main.iniciar)
        self.bloco1.addWidget(self.label)
        self.layout.addLayout(self.bloco1)

        #estilos
        self.label.setStyleSheet("QLabel"
                                        "{"
                                            "background-color: #2faa16;"
                                            "color: #ffffff;"
                                            "min-height: 80px;"
                                            "min-width: 300px;"
                                            "border-radius: 20px;"
                                            "font-size: 30px;"
                                            "text-align: center;"
                                            
                                        "}")

class TelaDicaDefine(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Sua vez')

        self.blocoA = QVBoxLayout()
        self.blocoA.addWidget(QLabel('Tema'))
        self.temaInput = QLineEdit()
        self.blocoA.addWidget(self.temaInput)
        self.blocoA.addWidget(QLabel('Dica'))
        self.dicaInput = QLineEdit()
        self.blocoA.addWidget(self.dicaInput)
        self.blocoA.addWidget(QLabel('Resposta'))
        self.respostaInput = QLineEdit()
        self.respostaInput.setStyleSheet("QLineEdit"
                                    "{"
                                    "margin-bottom: 80px;"
                                    "}")
        self.blocoA.addWidget(self.respostaInput)

        self.blocoB = QVBoxLayout()
        self.iniciarRodadaBtn = QPushButton('Iniciar Rodada')
        self.iniciarRodadaBtn.setStyleSheet("QPushButton"
                                    "{"
                                        "color: #ffffff;"
                                        "text-align: center;"
                                        #"background-color: #2faa16;"
                                        "background-color: green;"
                                        #"heigth: 40px;"
                                    "}")
        self.blocoB.addWidget(self.iniciarRodadaBtn)
        self.timer = QProgressBar()
        self.timer.setValue(100)
        self.timer.setStyleSheet("QProgressBar"
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
        self.timer.setFormat('60 segundos')
        self.blocoB.addWidget(self.timer)
        self.blocoB.setContentsMargins(0, 150, 0, 5)

        self.layout.addLayout(self.blocoA)
        self.layout.addLayout(self.blocoB)

class TelaJogo(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        
        self.divEsquerda = QVBoxLayout()
        self.divDireita = QVBoxLayout()

        self.bloco1 = QVBoxLayout()
        self.LabelJogadores = QLabel('Jogadores')
        self.LabelJogadores.setAlignment(QtCore.Qt.AlignCenter)
        self.bloco1.addWidget(self.LabelJogadores)
        self.caixaJogadores = QTextEdit()
        self.caixaJogadores.setReadOnly(True)
        self.bloco1.addWidget(self.caixaJogadores)

        self.bloco2 = QVBoxLayout()
        self.dicaLabel = QLabel('Texto com x letras')
        self.dicaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.pistaCaixa = QTextEdit()
        self.pistaCaixa.setReadOnly(True)
        self.bloco2.addWidget(self.dicaLabel)
        self.bloco2.addWidget(self.pistaCaixa)

        self.bloco3 = QVBoxLayout()
        self.LabelLog = QLabel("Log")
        self.LabelLog.setAlignment(QtCore.Qt.AlignCenter)
        self.bloco3.addWidget(self.LabelLog)
        self.caixaResposta = QTextEdit()
        self.caixaResposta.setReadOnly(True)
        self.caixaResposta.setStyleSheet("QScrollBar:vertical"
                                    "{"
                                        "background: #ffffff;"
                                        "color: #ffffff;"
                                        "border: 0px solid #ffffff;"
                                    "}"
                                    "QScrollBar::handle:vertical"
                                    "{"
                                        # "background: #7ba4da;"
                                        # "border: 1px solid #7ba4da;"
                                        "background: #ffffff;"
                                        "border: 1px solid gray;"
                                        "border-radius: 6px;"
                                    "}"
                                    "QScrollBar::add-line:vertical"
                                    "{"
                                        "width: 0px;"
                                        "height: 0px;"
                                    "}"
                                    "QScrollBar::sub-line:vertical"
                                    "{"
                                        "width: 0px;"
                                        "height: 0px;"
                                    "}"
                                    )
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

        self.tempo.setFormat('240 s') 
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
        self.setStyleSheet("QLabel"
                                    "{"
                                        "color: #1320d3;"
                                        "background-color: #ffffff;"
                                        "border: 1px solid gray;"
                                        "border-radius: 5px;"
                                        "padding: 2px;"
                                        "margin-bottom: 0px;"
                                        "text-align: center;"
                                    "}"
                            "QTextEdit"
                                    "{"
                                        "border-radius: 5px;"
                                        "margin-top: 0px;"
                                        "border: 1px solid gray;"
                                    "}"
                                    )


    def enviarResposta(self):
        resposta = self.tentativaRespostaInput.text()
        self.tentativaRespostaInput.setText('')
        self.main.client.send("!resposta,{}".format(resposta).encode('utf-8'))

    def printLog(self, resposta, ap):
        print("[print-log]\n")
        if(resposta == 'acertou'):
            if(ap == self.main.apelido == ap):
                self.caixaResposta.append("<span style=\"color: green;\">Você acertou!</span>")
            else:   self.caixaResposta.append("<span style=\"color: green;\">{} acertou!</span>".format(ap))
        else:
            self.caixaResposta.append("<span style=\"color: gray;\">{}</span>".format(resposta))


    # def definirTema(self):
    #     dlg = QDialog()
    #     dlg.setGeometry(20, 80, 400, 500)
    #     dlgLayout = QVBoxLayout()
    #     dlg.setLayout(dlgLayout)
    #     dlg.setWindowTitle('Sua vez')

    #     blocoA = QVBoxLayout()
    #     blocoA.addWidget(QLabel('Tema'))
    #     temaInput = QLineEdit()
    #     blocoA.addWidget(temaInput)
    #     blocoA.addWidget(QLabel('Dica'))
    #     dicaInput = QLineEdit()
    #     blocoA.addWidget(dicaInput)
    #     blocoA.addWidget(QLabel('Resposta'))
    #     respostaInput = QLineEdit()
    #     respostaInput.setStyleSheet("QLineEdit"
    #                                 "{"
    #                                 "margin-bottom: 80px;"
    #                                 "}")
    #     blocoA.addWidget(respostaInput)

    #     blocoB = QVBoxLayout()
    #     iniciarRodadaBtn = QPushButton('Iniciar Rodada')
    #     blocoB.addWidget(iniciarRodadaBtn)
    #     timer = QProgressBar()
    #     timer.setValue(100)
    #     timer.setStyleSheet("QProgressBar"
    #                                 "{"
    #                                     "color: #ffffff;"
    #                                     "text-align: center;"
    #                                     "background-color: #b2b2b6;"
    #                                     #"heigth: 40px;"
    #                                 "}"
    #                                 "QProgressBar::chunk"
    #                                 "{"
    #                                     "background-color: #1320d3"
    #                                 "}"
    #                                 )
    #     blocoB.addWidget(timer)

    #     dlgLayout.addLayout(blocoA)
    #     dlgLayout.addLayout(blocoB)

    #     dlg.exec_()

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

        self.setStyleSheet("background-color: #ffffff;")
        
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
            #self.tela_conexao.apelido_input.setReadOnly(True)
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
        self.tela_dica_define = TelaDicaDefine(self)
        self.tela_dica_espera = TelaDicaEspera(self)

        self.stackedLayout.addWidget(self.tela_inicial)
        self.stackedLayout.addWidget(self.tela_conexao)
        self.stackedLayout.addWidget(self.tela_jogo)
        self.stackedLayout.addWidget(self.tela_dica_define)
        self.stackedLayout.addWidget(self.tela_dica_espera)
        
    def iniciar(self):
        #startar controlador geral
        self.switchPage(self.tela_conexao_index)

    def switchPage(self, page_index):
        self.stackedLayout.setCurrentIndex(page_index)
        if(page_index==2):
            self.setWindowTitle("Trivia Game !")
            self.setFixedWidth(600)
            self.setFixedHeight(500)
        elif(page_index==3):
            self.setFixedWidth(self.width)
            self.setFixedHeight(self.height)
            self.setWindowTitle("Sua vez !")
        else:
            self.setWindowTitle("Trivia Game !")
            self.setFixedWidth(self.width)
            self.setFixedHeight(self.height)

    def iniciarPartida(self):
        print("INICIANDO PARTIDA")
        self.client.send(f"!iniciar-partida".encode('utf-8'))

    def mountReceiver(self):
        self.thread = QThread() # Instanciando uma thread em paralelo à principal -> QAplication.exec
        self.receiver = Receptor()  # Instanciando um "trabalhador" objeto para trabalhar em outra thread
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
        self.receiver.printLog.connect(self.tela_jogo.printLog)
        self.receiver.definirTema.connect(self.definirTema)


    def definirTema(self, ap):
        if(ap == self.apelido):
            self.switchPage(3)
        else: self.switchPage(4)



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
        #self.app.setStyle('Breeze')
        self.app.exec()
        encerrar = True
        print("Saindo...")
        self.view.desconectar()


game = gameController()
