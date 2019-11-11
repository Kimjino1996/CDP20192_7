import sys, os, enum, filesys_tool

# QT5 Python Binding
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from fat32Test import *

class View():

    # generateView ... Generates text view for hexdump likedness.
    def generateView(self, text):
        space = ' '
        bigSpace = ' ' * 4

        rowSpacing = self.rowSpacing
        rowLength = self.rowLength

        offset = 0

        offsetText = ''
        mainText = ''

        if ext is 'PNG':
            byte_arr = QByteArray(text)
            pixmap = QPixmap()
            ok = pixmap.loadFromData(byte_arr, "PNG")
            assert ok

            self.asciiTextArea.setPixmap(pixmap)

        elif ext is 'JPG':
            byte_arr = QByteArray(text)
            pixmap = QPixmap()
            ok = pixmap.loadFromData(byte_arr, "JPG")
            assert ok

            self.asciiTextArea.setPixmap(pixmap)

        else:
            asciiText = ''
        

        for chars in range(1, len(text) + 1):
            byte = text[chars - 1]
            char = chr(text[chars - 1])

            # Asciitext 는 오른쪽 출력부
            if (ext not 'PNG') and (ext not 'JPG'):
                if char is ' ':
                    asciiText += '.'

                elif char is '\n':
                    asciiText += '!'

                else:
                    asciiText += char
            
            # main text 가 중앙에 있는것
            mainText += format(byte, '0' + str(self.byteWidth) + 'x')

            if chars % rowLength is 0:
                offsetText += format(offset, '08x') + '\n'
                mainText += '\n'
                
                if (ext not 'PNG') and (ext not 'JPG'):
                    asciiText += '\n'

            elif chars % rowSpacing is 0:
                mainText += space * 2

            else:
                mainText += space

            offset += len(char)

        self.offsetTextArea.setText(offsetText)
        self.mainTextArea.setText(mainText)

        if (ext not 'PNG') and (ext not 'JPG'):
            self.asciiTextArea.setText(pixmap)

    

    # createMainView ... Creates the primary view and look of the application (3-text areas.)
    def createMainView(self):
        qhBox = QHBoxLayout()
        qhBox2 = QHBoxLayout()
        qvBox = QVBoxLayout()

        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath('')
        self.fileModel = QFileSystemModel()
        self.tree = QTreeView()
        self.list = QListView()
        self.tree.setModel(self.dirModel)
        self.list.setModel(self.fileModel)

        self.tree.clicked.connect(self.tree_on_clicked)
        self.list.clicked.connect(self.list_on_clicked)

        self.mainTextArea = QTextEdit()
        self.offsetTextArea = QTextEdit()
        if fat.ext is 'PNG' or 'JPG':
            self.asciiTextArea = QLabel()
        else:
            self.asciiTextArea = QTextEdit()


        # Initialize them all to read only.
        self.mainTextArea.setReadOnly(True)
        self.offsetTextArea.setReadOnly(True)
        if (fat.ext not 'PNG') and (fat.ext not 'JPG'):
            self.asciiTextArea.setReadOnly(True)
        

        # Create the fonts and styles to be used and then apply them.
        font = QFont("Consolas", 11, QFont.Normal, False)

        self.mainTextArea.setFont(font)
        self.offsetTextArea.setFont(font)
        if (fat.ext not 'PNG') and (fat.ext not 'JPG'):
            self.asciiTextArea.setFont(font)

        if (fat.ext not 'PNG') and (fat.ext not 'JPG'):
            # Syncing scrolls.
            filesys_tool.syncScrolls(self.mainTextArea, self.asciiTextArea, self.offsetTextArea)

            # Highlight linking. BUG-GY
            self.mainTextArea.selectionChanged.connect(filesys_tool.highlightMain)
            self.asciiTextArea.selectionChanged.connect(filesys_tool.highlightAscii)

        qhBox.addWidget(self.offsetTextArea, 1)
        qhBox.addWidget(self.mainTextArea, 6)
        qhBox.addWidget(self.asciiTextArea, 2)
        qhBox2.addWidget(self.tree)
        qhBox2.addWidget(self.list)
        qvBox.addLayout(qhBox2)
        qvBox.addLayout(qhBox)
        return qvBox

if __name__ == '__main__':
    fat = fat32Test.FAT32('fat32.dd')
