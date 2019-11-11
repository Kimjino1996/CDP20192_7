import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class File_Icon(QWidget):

    def __init__(self,name,left=10,top=10,width=320,height=200):
        super().__init__()
        self.title = 'PyQt5 button - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.button_create(name)


    def button_create(self,name):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        button=QPushButton(name,self)
        button.setIcon(self.style().standardIcon(getattr(QStyle,'SP_DirIcon')))
        button.setToolTip('This is an example button')
        button.setStyleSheet("color: black;"
                        "background-color: white;"
                             );

        button.move(100, 70)
        button.clicked.connect(self.on_click)

        self.show()

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    for i in range(10):
        ex = File_Icon("dir")

    sys.exit(app.exec_())