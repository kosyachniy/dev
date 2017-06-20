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

class but(QWidget):
    def __init__(self, parent):
        super(but, self).__init__(parent)

#Кнопки в нижнем углу
        b1=QPushButton('OK',self)
        b2=QPushButton('CANCEL',self)

        b1.clicked.connect(self.click)
        b2.clicked.connect(self.click)

        hbox=QHBoxLayout(self) #Вертикальный блок
        hbox.addStretch() #Бесконечное пустое растяжение
        hbox.addWidget(b1)
        hbox.addWidget(b2)

        self.setLayout(hbox)

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