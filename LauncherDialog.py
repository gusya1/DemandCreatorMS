from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog

from ui.ui_LauncherDialog import Ui_LauncherDialog
from SettingsDialog import SettingsDialog


class LauncherDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.ui = Ui_LauncherDialog()
        self.ui.setupUi(self)

        self.ui.btnSettings.clicked.connect(self.open_settings)

    @QtCore.pyqtSlot()
    def open_settings(self):
        settings_dialog = SettingsDialog()
        self.hide()
        settings_dialog.exec()
        self.show()

