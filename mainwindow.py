import datetime
import os

from MSApi import DateTimeFilter, MSApi, CustomerOrder, create_demand, get_demand_template_by_customer_order, \
    MSApiException, Filter, Expand
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QInputDialog
# from PyQt5 import QtGui
# from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
# from PyQt5.QtCore import QMarginsF
from ui.ui_mainwindow import Ui_MainWindow
import configparser


class MainWindow(QMainWindow):

    MS_SETTINGS_SECTION = 'moy_sklad_settings'
    MS_AUCH_TOKEN_OPTION = 'auch_token'
    MS_PROJ_BLACKLIST_ENTITY_OPTION = 'project_blacklist_entity_name'

    def __error(self, err):
        QtWidgets.QMessageBox.critical(self, "Error", str(err))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionSet_MS_token.triggered.connect(self.on_set_ms_token_triggered)
        self.ui.actionSet_status_blacklist_entity.triggered.connect(self.on_set_blacklist_entity_triggered)

        self.ui.btnGenerate.clicked.connect(self.on_btnGenerateClicked)

        try:
            settings_dir_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            if not os.path.exists(settings_dir_path):
                os.makedirs(settings_dir_path)
            self.settings_path = settings_dir_path + "/settings.ini"

            if not os.path.exists(self.settings_path):
                file = open(self.settings_path, "w")
                file.close()
        except OSError as e:
            raise RuntimeError("Settings file create failed: {}".format(str(e)))

        self.config = configparser.ConfigParser()
        self.config.read_dict({self.MS_SETTINGS_SECTION: {
            self.MS_AUCH_TOKEN_OPTION: "",
            self.MS_PROJ_BLACKLIST_ENTITY_OPTION: ""
        }})
        self.config.read(self.settings_path)
        section = self.config[self.MS_SETTINGS_SECTION]
        ms_auch_key = section[self.MS_AUCH_TOKEN_OPTION]
        if not ms_auch_key:
            QtWidgets.QMessageBox.warning(self, "Warning", "MS token is empty!\nPlease, enter MS token.")
            self.on_set_ms_token_triggered()
        else:
            MSApi.set_access_token(ms_auch_key)

        self.project_blacklist = []
        name_of_entity_proj_blacklist = section[self.MS_PROJ_BLACKLIST_ENTITY_OPTION]
        if not name_of_entity_proj_blacklist:
            QtWidgets.QMessageBox.warning(self, "Warning", "Blacklist entity is empty!\nPlease, choose entity")
            self.on_set_blacklist_entity_triggered()
        else:
            self.__fill_project_blacklist()

    def __fill_project_blacklist(self):
        try:
            entity_name = self.config[self.MS_SETTINGS_SECTION][self.MS_PROJ_BLACKLIST_ENTITY_OPTION]
            for entity in MSApi.get_company_settings().gen_custom_entities():
                if entity.get_name() != entity_name:
                    continue
                self.project_blacklist = list(entity_elem.get_name() for entity_elem in entity.gen_elements())
                break
            else:
                self.__error("Entity {} not found! Please, choose another.")
                self.on_set_blacklist_entity_triggered()
        except MSApiException as e:
            self.__error(str(e))

    def __write_config(self):
        file = open(self.settings_path, "w")
        self.config.write(file)
        file.close()

    @QtCore.pyqtSlot()
    def on_set_ms_token_triggered(self):
        ms_token, action = QInputDialog.getText(self, "Enter MS token", "token")
        self.config[self.MS_SETTINGS_SECTION][self.MS_AUCH_TOKEN_OPTION] = ms_token
        MSApi.set_access_token(ms_token)
        self.__write_config()

    @QtCore.pyqtSlot()
    def on_set_blacklist_entity_triggered(self):
        try:
            entity_names_list = list(entity.get_name() for entity in MSApi.get_company_settings().gen_custom_entities())
            entity_name, action = QInputDialog.getItem(self, "Choose project blacklist entity", "Entity:",
                                                       entity_names_list, editable=False)
            self.config[self.MS_SETTINGS_SECTION][self.MS_PROJ_BLACKLIST_ENTITY_OPTION] = entity_name
            self.__fill_project_blacklist()
            self.__write_config()
        except MSApiException as e:
            self.__error(str(e))

    @QtCore.pyqtSlot()
    def on_btnGenerateClicked(self):
        try:
            error_list = []

            date = self.ui.calendarWidget.selectedDate().toPyDate()
            dt = datetime.datetime.combine(date, datetime.time.min)
            co_filter = DateTimeFilter.gte('deliveryPlannedMoment', dt)
            co_filter += DateTimeFilter.lt('deliveryPlannedMoment', dt + datetime.timedelta(days=1))

            total_count = 0
            for customer_order in MSApi.gen_customer_orders(filters=co_filter, expand=Expand("project")):
                customer_order: CustomerOrder
                if next(customer_order.gen_demands(), None) is not None:
                    continue
                project = customer_order.get_project()
                if project is not None:
                    if project.get_name() in self.project_blacklist:
                        continue
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



