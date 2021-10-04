
from MSApi import MSApi, MSApiException
from PyQt5 import QtWidgets
import sys
from mainwindow import MainWindow
from MSApi import MSApi


def fatal_error(message):
    QtWidgets.QMessageBox.critical(None, "Error", str(message))
    app.exit(1)
    exit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("DemandCreatorMS")

    try:

        window = MainWindow()
        window.show()

    except MSApiException as e:
        fatal_error(e)
    except RuntimeError as e:
        fatal_error(e)

    app.exec()
