import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QDesktopWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap

class window(QWidget): #QMainWindow
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ZODZU') #Название окна
        q=QDesktopWidget().availableGeometry()
        self.setGeometry(0, 0, q.width(), q.height()) #Размеры окна и положение

#Верхняя полоса
        p1=QPixmap("icon.png")
        t1=QLabel(self)
        t1.setPixmap(p1)
        t2=QLabel('ZODZU', self) #Надпись

        b3=QPushButton('Notes',self)
        b3.clicked.connect(self.click)

        l1=QHBoxLayout()
        l1.addWidget(t1)
        l1.addWidget(t2)
        l1.addWidget(b3)
        l1.addStretch()

#Кнопки в нижнем углу
        b1=QPushButton('OK',self)
        b2=QPushButton('CANCEL',self)

        b1.clicked.connect(self.click)
        b2.clicked.connect(self.click)

        hbox=QHBoxLayout() #Вертикальный блок
        hbox.addStretch() #Бесконечное пустое растяжение
        hbox.addWidget(b1)
        hbox.addWidget(b2)

        vbox=QVBoxLayout()
        vbox.addLayout(l1)
        vbox.addStretch()
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def click(self): #Обработка кликов
        sender=self.sender()
        if sender.text()=='Notes':
            t3=QLabel('Note', self)
            self.vbox.addWidget(t3)
#            self.statusBar().showMessage('123')

if __name__ == '__main__':
    app=QApplication(sys.argv)

    x=window()
#   x2=bar()
    x.show()
    
    sys.exit(app.exec_())