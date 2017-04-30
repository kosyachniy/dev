import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication, QAction, qApp, QTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QGridLayout
from PyQt5.QtGui import QFont, QIcon

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
#Текст
        l1=QLabel('Hello world!',self)
        l1.move(15, 10)
#Кнопка
        b3=QPushButton('Push me',self)
        b3.move(15, 50)
        
        b3.clicked.connect(self.click)
        self.statusBar()
#Ввод текста
        textEdit=QTextEdit()
#        self.setCentralWidget(textEdit)
#Окно
#       w=QWidget()
#       w.resize(250, 150)
#       w.move(300, 300)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('UPLe')
        self.show()
#При нажатии кнопки
    def click(self):
        sender=self.sender()
        if sender.text()=='Push me':
            self.statusBar().showMessage('123')

class first(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
#Текстовые поля
        title=QLabel('Title')
        author=QLabel('Author')
        review=QLabel('Review')

        titleEdit=QLineEdit()
        authorEdit=QLineEdit()
        reviewEdit=QTextEdit()

        grid=QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid)

if __name__ == '__main__':
    app=QApplication(sys.argv)

#    x=first()
    x=main()
    
    sys.exit(app.exec_())