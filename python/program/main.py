import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class first(QWidget):
    def __init__(self):
        super().__init__()

        window = QDesktopWidget().availableGeometry()
        self.width = window.width()
        self.height = window.height()

        self.initUI()

    '''
# Фон
    def resizeEvent(self, event):
        palette = QPalette()
        img = QImage('1.png')
        scaled = img.scaled(self.size(), Qt.KeepAspectRatioByExpanding, transformMode = Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled))
        self.setPalette(palette)
    '''

    def initUI(self):
# Считывание контента
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
        q = QDesktopWidget().availableGeometry()
        for i in self.x:
# Кнопки
            if i[:7] == '@button':
                self.b.append(QPushButton(i[8:-1], self))
                self.b[len(self.b) - 1].clicked.connect(self.click)
                # self.b[len(self.b) - 1].setFixedWidth(500)
                self.b[len(self.b) - 1].setFixedHeight(60)
# Изображения
            elif i[:6] == '@image':
                lbl = QLabel(self)
                lbl.setPixmap(QPixmap(i[7:-1]))
                self.b.append(lbl)
# Заголовок
            elif i[:6] == '@title':
                lbl = QLabel('<div style="font-size: 40px; text-align: center;">' + i[7:-1] + '</div>')
                self.b.append(lbl)
# Текст
            else:
                lbl = QLabel(i)
                self.b.append(lbl)

# Разметка страницы
        vbox = QVBoxLayout()
        for i in range(len(self.b)):
            vbox.addWidget(self.b[i])
        self.setLayout(vbox)

# Параметры окна
        self.setGeometry(self.width * 0.2, self.height * 0.2, self.width * 0.6, self.height * 0.6)
        self.setWindowTitle('Goncharov Lox')
        # self.setWindowIcon(QIcon('icon.png'))
        self.show()

# Обработка кликов
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