import json
import os

from PyQt5.QtCore import QStandardPaths
from PyQt5.QtWidgets import QDialog

from ui.ui_SettingsDialog import Ui_SettingsDialog
import settings


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.settings_path = self.__get_settings_path()

        settings_file = open(self.settings_path, "r")
        settings.SETTINGS = json.load(settings_file)
        ms_auch_token = settings.SETTINGS.get("ms_auch_token")





    @staticmethod
    def __get_settings_path():
        try:
            settings_dir_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            if not os.path.exists(settings_dir_path):
                os.makedirs(settings_dir_path)
            settings_path = settings_dir_path + "/settings.json"

            if not os.path.exists(settings_path):
                file = open(settings_path, "w")
                file.close()

            return settings_path

        except OSError as e:
            raise RuntimeError("Settings file create failed: {}".format(str(e)))
