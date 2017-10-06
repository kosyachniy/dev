import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QHBoxLayout, QVBoxLayout, QDesktopWidget, QLabel
from PyQt5.QtGui import QPixmap

class first(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
#Считывание контента
        with open('set.txt', 'r') as file:
            win = file.read()

        try:
            with open(win + '.txt', 'r') as file:
                self.x = file.read().split('\n')
        except:
            with open('main.txt', 'r') as file:
                self.x = file.read().split('\n')

        #print(self.x)

        self.b = []
        for i in self.x:
#Кнопки
            if i[:7] == '@button':
                self.b.append(QPushButton(i[8:-1], self))
                self.b[len(self.b) - 1].clicked.connect(self.click)
#Изображения
            elif i[:6] == '@image':
                lbl = QLabel(self)
                lbl.setPixmap(QPixmap(i[7:-1]))
                self.b.append(lbl)
#Текст
            else:
                lbl = QLabel(i)
                self.b.append(lbl)

#Разметка страницы
        hbox = QVBoxLayout()
        for i in range(len(self.b)):
            hbox.addWidget(self.b[i])
        vbox = QHBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

#Параметры окна
        q = QDesktopWidget().availableGeometry()
        self.setGeometry(0, 0, q.width(), q.height())
        self.setWindowTitle('Goncharov Lox')
        self.show()

#Обработка кликов
    def click(self):
        with open('set.txt', 'w') as file:
            print(self.sender().text(), end='', file=file)

        if self.sender().text() == 'Выход':
            sys.exit(app.exec_())

        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    while True:
        x = first()
        app.exec_()