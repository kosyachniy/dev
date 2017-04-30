import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
class main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
#Текст
        ###

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('UPLe')
        self.show()
#При закрытии окна спрашивает
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Are you sure to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app=QApplication(sys.argv)

    x=main()
    
    sys.exit(app.exec_())