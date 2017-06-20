import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget


if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = QWidget()
    q=QDesktopWidget().availableGeometry()
    w.setGeometry(0, 0, q.width(), q.height())
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())