
from MSApi import MSApi, MSApiException
from PyQt5 import QtWidgets
import sys
from mainwindow import MainWindow
from MSApi import MSApi


import settings

def fatal_error(message):
    QtWidgets.QMessageBox.critical(None, "Error", str(message))
    app.exit(1)
    exit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    try:
        MSApi.set_access_token(settings.MOY_SKLAD.TOKEN)

        window = MainWindow()
        window.show()
    except MSApiException as e:
        fatal_error(e)

    app.exec()
