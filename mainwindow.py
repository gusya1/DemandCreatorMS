import datetime

from MSApi import DateTimeFilter, MSApi, MSApiException, Expand, Store, Filter
from MSApi.documents.ProcessingOrder import ProcessingOrder, Processing
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
# from PyQt5 import QtGui
# from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
# from PyQt5.QtCore import QMarginsF
from ui.ui_mainwindow import Ui_MainWindow
from settings import MOY_SKLAD


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

        for entity in MSApi.get_company_settings().gen_custom_entities():
            if entity.get_name() != MOY_SKLAD.PROCESSING_PLAN_BLACKLIST_ENTITY:
                continue
            self.processing_plan_blacklist = list(entity_elem.get_name() for entity_elem in entity.gen_elements())
            break
        else:
            raise RuntimeError("Entity {} not found!".format(MOY_SKLAD.PROCESSING_PLAN_BLACKLIST_ENTITY))

        for store in Store.generate(filters=Filter.eq('name', MOY_SKLAD.STORE_NAME)):
            self.store = store
            break
        else:
            raise RuntimeError("Store {} not found!".format(MOY_SKLAD.STORE_NAME))

    @QtCore.pyqtSlot()
    def on_btnGenerateClicked(self):
        try:
            error_list = []

            date = self.ui.calendarWidget.selectedDate().toPyDate()
            dt = datetime.datetime.combine(date, datetime.time.min)
            date_filter = DateTimeFilter.gte('deliveryPlannedMoment', dt)
            date_filter += DateTimeFilter.lt('deliveryPlannedMoment', dt + datetime.timedelta(days=1))

            total_count = 0
            for processing_order in ProcessingOrder.generate(filters=date_filter, expand=Expand("processingPlan")):
                processing_order: ProcessingOrder
                if next(processing_order.gen_processings(), None) is not None:
                    continue
                processing_plan = processing_order.get_processing_plan()
                if processing_plan.get_name() in self.processing_plan_blacklist:
                    continue
                total_count += 1
                try:
                    template = Processing.get_template_by_processing_order(processing_order)
                    template.get_json()["productsStore"] = {'meta': self.store.get_meta().get_json()}
                    template.get_json()["materialsStore"] = {'meta': self.store.get_meta().get_json()}
                    po_quantity = processing_order.get_quantity()
                    template.get_json()["quantity"] *= po_quantity
                    for product in template.get_json()["products"]["rows"]:
                        product["quantity"] *= po_quantity
                    for material in template.get_json()["materials"]["rows"]:
                        material["quantity"] *= po_quantity

                    Processing.create(template)
                except MSApiException as e:
                    error_list.append("Processing for {} processing order create failed: {}"
                                      .format(processing_order.get_name(), str(e)))

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



