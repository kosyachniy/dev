import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon

class first(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('UPLe')
        self.setWindowIcon(QIcon('icon.png'))
        self.show()

if __name__ == '__main__':
    app=QApplication(sys.argv)

    x=first()

    sys.exit(app.exec_())