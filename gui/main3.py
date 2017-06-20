import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QDesktopWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)

        self.setWindowTitle('ZODZU') #Название окна
        q=QDesktopWidget().availableGeometry()
        w=q.width()
        h=q.height()
        self.setGeometry(0, 0, w, h) #Размеры окна и положение

        self.form_widget=but(self)

class bar(QWidget):
    def __init__(self, parent):
        super(bar, self).__init__(parent)

#Верхняя полоса
        self.layout=QHBoxLayout(self)
        self.button1=QPushButton("Button 1")
        self.layout.addWidget(self.button1)
#        label=QLabel('123', self) #Надпись
#        label.setGeometry(0, 0, q.width(), 50)


class but(QWidget):
    def __init__(self, parent):
        super(but, self).__init__(parent)

        q=QDesktopWidget().availableGeometry()
        w=q.width()
        h=q.height()
        self.setGeometry(0, 0, w, h)

#Кнопки в нижнем углу
        self.b1=QPushButton('OK',self)
        self.b2=QPushButton('CANCEL',self)

        self.b1.clicked.connect(self.click)
        self.b2.clicked.connect(self.click)

        self.hbox=QHBoxLayout(self) #Вертикальный блок
        self.hbox.addStretch() #Бесконечное пустое растяжение
        self.hbox.addWidget(self.b1)
        self.hbox.addWidget(self.b2)

        self.vbox=QVBoxLayout(self)
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)

    def click(self): #Обработка кликов
        sender=self.sender()
        if sender.text()=='OK':
            print('123')


if __name__ == '__main__':
    app=QApplication(sys.argv)

    x=window()
#   x2=bar()
    x.show()
    
    sys.exit(app.exec_())