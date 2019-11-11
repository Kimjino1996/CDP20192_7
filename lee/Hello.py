import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
class Exam(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setGeometry(300,300,400,500)#창크기 조절
        self.btnList=[]
        self.btnTop=100
        self.cnt=0

        self.lbl= QLabel("??",self)
        self.lbl.move(10,10)

        self.txt =QLineEdit("",self)
        self.txt.move(10,self.lbl.height())

        self.btn = QPushButton("버튼생성",self)
        self.btn.resize(QSize(80,25))
        self.btn.move(10,self.lbl.height() + self.txt.height())

        self.btn.clicked.connect(self.createBtn) #연결해야함

        self.show()

    def createBtn(self):
         self.cnt = int(self.txt.text())
         for i in range(self.cnt):
            self.btnList.append((QPushButton(str(i+1)),self))
            self.btnList[i].resize(QSize(80,25))
            self.btnList[i].move(10,self.btnTop+(i*25))
            self.btnList[i].show()
app = QApplication([]) #어플리케이션 객체 생성
w= Exam()
sys.exit(app.exec_()) #나갈때

