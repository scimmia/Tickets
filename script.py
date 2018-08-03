import datetime
import os
import xlsxwriter

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tickets.settings") #加载项目环境，"BMS.settings"为项目配置文件

import django     #加载django
django.setup()#启动django

from ticket import models

def buildDailyReport():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    workbook = xlsxwriter.Workbook('static/dailyreport/%s.xlsx' % (today))
    date_format = workbook.add_format({'num_format': 'yyyy/mm/dd', 'align': 'left'})
    worksheet = workbook.add_worksheet(u'日报表')
    worksheet.set_column('A:A', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('J:J', 20)
    worksheet.write(0, 0, u'购买日期')
    worksheet.write(0, 1, u'前排票号')
    worksheet.write(0, 2, u'票号')
    worksheet.write(0, 3, u'出票行')
    worksheet.write(0, 4, u'出票日期')
    worksheet.write(0, 5, u'到期日期')
    worksheet.write(0, 6, u'票面价格')
    worksheet.write(0, 7, u'购入价格')
    worksheet.write(0, 8, u'供应商')
    worksheet.write(0, 9, u'卖出日期')
    worksheet.write(0, 10, u'卖出价格')
    worksheet.write(0, 11, u'买票人')
    worksheet.write(0, 12, u'利润')

    tickets = models.Ticket.objects.all()
    print(tickets)
    for inx,t in enumerate(tickets):
        worksheet.write(inx+1, 0, t.goumairiqi,date_format)
        worksheet.write(inx+1, 1, t.qianpaipiaohao)
        worksheet.write(inx+1, 2, t.piaohao)
        worksheet.write(inx+1, 3, t.chupiaohang)
        worksheet.write(inx+1, 4, t.chupiaoriqi,date_format)
        worksheet.write(inx+1, 5, t.daoqiriqi,date_format)
        worksheet.write(inx+1, 6, t.piaomianjiage)
        worksheet.write(inx+1, 7, t.gourujiage)
        worksheet.write(inx+1, 8, t.gongyingshang)
        worksheet.write(inx+1, 9, t.maichuriqi,date_format)
        worksheet.write(inx+1, 10, t.maichujiage)
        worksheet.write(inx+1, 11, t.maipiaoren)
        worksheet.write(inx+1, 12, t.lirun)

    worksheet = workbook.add_worksheet(u'日报表1')
    worksheet.set_column('A:A', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('J:J', 20)
    worksheet.write(0, 0, u'购买日期')
    worksheet.write(0, 1, u'前排票号')
    worksheet.write(0, 2, u'票号')
    worksheet.write(0, 3, u'出票行')
    worksheet.write(0, 4, u'出票日期')
    worksheet.write(0, 5, u'到期日期')
    worksheet.write(0, 6, u'票面价格')
    worksheet.write(0, 7, u'购入价格')
    worksheet.write(0, 8, u'供应商')
    worksheet.write(0, 9, u'卖出日期')
    worksheet.write(0, 10, u'卖出价格')
    worksheet.write(0, 11, u'买票人')
    worksheet.write(0, 12, u'利润')

    tickets = models.Ticket.objects.all()
    print(tickets)
    for inx,t in enumerate(tickets):
        worksheet.write(inx+1, 0, t.goumairiqi,date_format)
        worksheet.write(inx+1, 1, t.qianpaipiaohao)
        worksheet.write(inx+1, 2, t.piaohao)
        worksheet.write(inx+1, 3, t.chupiaohang)
        worksheet.write(inx+1, 4, t.chupiaoriqi,date_format)
        worksheet.write(inx+1, 5, t.daoqiriqi,date_format)
        worksheet.write(inx+1, 6, t.piaomianjiage)
        worksheet.write(inx+1, 7, t.gourujiage)
        worksheet.write(inx+1, 8, t.gongyingshang)
        worksheet.write(inx+1, 9, t.maichuriqi,date_format)
        worksheet.write(inx+1, 10, t.maichujiage)
        worksheet.write(inx+1, 11, t.maipiaoren)
        worksheet.write(inx+1, 12, t.lirun)
    workbook.close()
    pass

buildDailyReport()