import configparser
import os
from PyQt5.QtCore import QStandardPaths


class MOY_SKLAD:
    TOKEN = ""
    PROCESSING_PLAN_BLACKLIST_ENTITY = ""
    STORE_NAME = ""


def read_config():
    config = configparser.ConfigParser()
    settings_dir = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
    config.read_dict(
        {
            'moy_sklad_auch': {
                'auch_token': "",
            },
            'processing_generator': {
                'processing_plan_blacklist_entity': "",
                'store_name': ""
            }
        })

    settings_path = settings_dir + "/ms_settings.ini"
    if not os.path.exists(settings_path):
        os.makedirs(settings_dir, exist_ok=True)
        file = open(settings_path, 'w')
        config.write(file)

    config.read(settings_path, encoding="utf-8")
    section = config['moy_sklad_auch']
    MOY_SKLAD.TOKEN = section['auch_token']
    section = config['processing_generator']
    MOY_SKLAD.PROCESSING_PLAN_BLACKLIST_ENTITY = section['processing_plan_blacklist_entity']
    MOY_SKLAD.STORE_NAME = section['store_name']


read_config()