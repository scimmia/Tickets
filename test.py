import datetime
import os
import xlsxwriter
from django.db.models import Q

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tickets.settings") #加载项目环境，"BMS.settings"为项目配置文件

import django     #加载django
django.setup()#启动django

from ticket import models, utils

import logging

# logging.basicConfig(filename='example.log', level=logging.DEBUG)
logging.basicConfig(filename='example.log', level=logging.DEBUG,format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)



def dailyJob():
    try:
        logger.info('info1')
        logger.error('info')
        logger.warning('info2')
    except:
        pass
    pass

dailyJob()
