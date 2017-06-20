import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QHBoxLayout, QVBoxLayout

class first(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
#Кнопки в нижнем углу
        b1=QPushButton('OK',self)
        b2=QPushButton('CANCEL',self)

        b1.clicked.connect(self.click)
        b2.clicked.connect(self.click)

        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(b1)
        hbox.addWidget(b2)

        vbox=QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('UPLe')
        self.show()
    def click(self):
        sender=self.sender()
        if sender.text()=='OK':
            print('123')

if __name__ == '__main__':
    app=QApplication(sys.argv)

    x=first()
    
    sys.exit(app.exec_())