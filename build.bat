pyrcc5.exe -o rc\resources_rc.py resources.qrc
pyuic5.exe mainwindow.ui -o ui\ui_mainwindow.py --import-from=rc
pyuic5.exe SettingsDialog.ui -o ui/ui_SettingsDialog.py --import-from=rc
pyuic5.exe LauncherDialog.ui -o ui/ui_LauncherDialog.py --import-from=rc
#venv\Scripts\python.exe -m PyInstaller --onefile --icon pictures\icon.ico -w --paths venv\Lib\site-packages -n MapGeneratorMS main.py