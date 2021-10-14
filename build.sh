pip3 install --target=venv -r requirements.txt

venv/bin/pyrcc5 -o rc/resources_rc.py resources.qrc
venv/bin/pyuic5 mainwindow.ui -o ui/ui_mainwindow.py --import-from=rc
python3 -m PyInstaller --onefile --icon pictures\icon.ico -w --paths venv\Lib\site-packages -n ProcessingCreatorMS main.py