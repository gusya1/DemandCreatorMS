venv/bin/pyrcc5 -o rc/resources_rc.py resources.qrc
venv/bin/pyuic5 mainwindow.ui -o ui/ui_mainwindow.py --import-from=rc
venv/bin/pyuic5 SettingsDialog.ui -o ui/ui_SettingsDialog.py --import-from=rc
venv/bin/pyuic5 LauncherDialog.ui -o ui/ui_LauncherDialog.py --import-from=rc
venv/bin/python3.7 -m PyInstaller --onefile --icon pictures\icon.ico -w --paths venv\Lib\site-packages -n DemandCreatorMS main.py