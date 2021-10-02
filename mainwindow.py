import datetime

from MSApi import DateTimeFilter, MSApi, CustomerOrder, create_demand, get_demand_template_by_customer_order, \
    MSApiException
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
# from PyQt5 import QtGui
# from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
# from PyQt5.QtCore import QMarginsF
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):

    def __error(self, err):
        QtWidgets.QMessageBox.critical(self, "Error", str(err))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btnGenerate.clicked.connect(self.on_btnGenerateClicked)

        self.download_location = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.DownloadLocation)

    @QtCore.pyqtSlot()
    def on_btnGenerateClicked(self):
        try:
            error_list = []

            date = self.ui.calendarWidget.selectedDate().toPyDate()
            dt = datetime.datetime.combine(date, datetime.time.min)
            date_filter = DateTimeFilter.gte('deliveryPlannedMoment', dt)
            date_filter += DateTimeFilter.lt('deliveryPlannedMoment', dt + datetime.timedelta(days=1))

            total_count = 0
            for customer_order in MSApi.gen_customer_orders(filters=date_filter):
                customer_order: CustomerOrder
                if next(customer_order.gen_demands(), None) is None:
                    total_count += 1
                    try:
                        create_demand(get_demand_template_by_customer_order(customer_order))
                    except MSApiException as e:
                        error_list.append("Demand for {} customer order create failed: {}"
                                          .format(customer_order.get_name(), str(e)))

            if len(error_list) != 0:
                error_list_str = ""
                for i, error in enumerate(error_list):
                    error_list_str += f"<li><b>[{i}]</b> {error}</li>"
                QtWidgets.QMessageBox.critical(self, f"{len(error_list)} Errors", error_list_str)

            QtWidgets.QMessageBox.information(self, "Success", f"{total_count - len(error_list)}/{total_count}")

        except MSApiException as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))



