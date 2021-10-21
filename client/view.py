import sys
import time
import asyncio
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
#classe para gerenciar threads em paralelo à thread principal -> (QAplication.exec)
class WorkerTimeBarControl(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        print("\t[WorkerTimeBarControl.run()]")
        for i in range(100, -1, -1):
            time.sleep(0.3)
            self.progress.emit(i)
        self.finished.emit() #à definir: função a ser chamada após o fim do tempo -> inicioDoJogo ou Restart

class WorkerControleGeral(QObject):
    finished = pyqtSignal()


class myBtn(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("myBtn")
        #self.clicked.connect(self.test)
    def test(self):
        print('myBtn')


class TelaInicialLayout(QVBoxLayout):
    def __init__(self, start_controlador_geral):
        super().__init__()
        #
        self.bloco1 = QVBoxLayout()
        self.start_button = QPushButton('Começar')
        self.start_button.clicked.connect(start_controlador_geral)
        self.bloco1.addWidget(self.start_button)
        self.addLayout(self.bloco1)



class TelaConexaoLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        #Bloco 1
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
        self.conectar_botao.clicked.connect(lambda: self.timeBarControl())
        self.status_conexao = QLabel('Servidor não conectado')
        self.status_conexao.setText('<span style=\"color: gray;\">Servidor não conectado</span>')
        self.status_conexao.setAlignment(QtCore.Qt.AlignCenter)
        self.bloco2.addWidget(self.conectar_botao)
        self.bloco2.addWidget(self.status_conexao)

        #Bloco 3
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
                                        "background-color: #b2b2b6"
                                    "}"
                                    "QProgressBar::chunk"
                                    "{"
                                        "background-color: #1320d3"
                                    "}"
                                    )

        self.time_bar.setFormat('') 
        self.bloco4.addWidget(self.time_bar)

        #Adicionando bloco à tela
        self.addLayout(self.bloco1)
        self.addLayout(self.bloco2)
        self.addLayout(self.bloco3)
        self.addLayout(self.bloco4)

        print("[TelaInicialLayout Montada]")

    def timeBarControl(self):
        print("[timeBarControl]")
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
        self.time_bar.setFormat(f"{str(valor)} s") 
        self.time_bar.setAlignment(Qt.AlignCenter) 



class Tela(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trivia Game !")
        self.tela_inicial_index = 0
        self.tela_conexao_index = 1
        self.tela_jogo_index = 2
        self.tela_mestre_index = 3
        #enqudramento janela
        self.left = 20
        self.top = 80
        self.width = 400
        self.height = 500
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.mount()
        self.show()
        #self.statusBarControl(self.tela_inicial_layout.time_bar)
        

    def mount(self):
        
        # Create the stacked layout
        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)
        # Create the first page
        self.tela_conexao = QWidget()
        self.tela_conexao_layout = TelaConexaoLayout()
        self.tela_conexao.setLayout(self.tela_conexao_layout)

        


        # Create the second page
        self.tela_inicial = QWidget()
        self.tela_inicial_layout = TelaInicialLayout(self.startControladorGeral)
        self.tela_inicial.setLayout(self.tela_inicial_layout)
        #self.stackedLayout.addWidget(self.page2)
        # Add tela in the stacked layout
        self.stackedLayout.addWidget(self.tela_inicial)
        self.stackedLayout.addWidget(self.tela_conexao)
        
    
    def startControladorGeral(self):
        print("[start controlador geral]")
        #startar controlador geral
        self.switchPage(self.tela_conexao_index)

    def switchPage(self, page_index):
        self.stackedLayout.setCurrentIndex(page_index)


app = QApplication(sys.argv)
view = Tela()
sys.exit(app.exec())