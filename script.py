import datetime
import os
import xlsxwriter
import schedule
import time
from django.db.models import Q

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tickets.settings") #加载项目环境，"BMS.settings"为项目配置文件

import django     #加载django
django.setup()#启动django

from ticket import models

def writeHeader(workbook,worksheet):
    merge_format = workbook.add_format({
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',})
    ws = worksheet
    # worksheet.set_row(1, 20)
    worksheet.set_column('H:H', 10.11)
    worksheet.set_column('K:K', 10.11)
    ws.merge_range('A1:W2', '日报表', merge_format)
    ws.merge_range('B3:C4', '现金', merge_format)
    ws.merge_range('D3:E4', '存票', merge_format)
    ws.merge_range('F3:H4', '应收', merge_format)
    ws.merge_range('I3:K4', '应付', merge_format)
    ws.merge_range('L3:Q3', '费用', merge_format)
    ws.merge_range('L4:M4', '业务费用', merge_format)
    ws.merge_range('N4:O4', '资本费用', merge_format)
    ws.merge_range('P4:Q4', '管理杂费', merge_format)
    ws.merge_range('R3:W3', '利润', merge_format)
    ws.merge_range('R4:S4', '业务利润', merge_format)
    ws.merge_range('T4:U4', '资本收益', merge_format)
    ws.merge_range('V4:W4', '其他利润', merge_format)
    ws.write('B5','金额',merge_format)
    ws.write('C5','备注',merge_format)
    ws.write('D5','金额',merge_format)
    ws.write('E5','备注',merge_format)
    ws.write('F5','',merge_format)
    ws.write('G5','金额',merge_format)
    ws.write('H5','备注',merge_format)
    ws.write('I5','',merge_format)
    ws.write('J5','金额',merge_format)
    ws.write('K5','备注',merge_format)
    ws.write('L5','金额',merge_format)
    ws.write('M5','备注',merge_format)
    ws.write('N5','金额',merge_format)
    ws.write('O5','备注',merge_format)
    ws.write('P5','金额',merge_format)
    ws.write('Q5','备注',merge_format)
    ws.write('R5','金额',merge_format)
    ws.write('S5','备注',merge_format)
    ws.write('T5','金额',merge_format)
    ws.write('U5','备注',merge_format)
    ws.write('V5','金额',merge_format)
    ws.write('W5','备注',merge_format)
    ws.write('A6','合计',merge_format)
    pass
def buildDailyReport():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    workbook = xlsxwriter.Workbook('static/dailyreport/%s.xlsx' % (today))
    date_format = workbook.add_format({'num_format': 'yyyy/mm/dd', 'align': 'left'})
    worksheet = workbook.add_worksheet(u'日报表')
    writeHeader(workbook,worksheet)

    startrow = 6

    cards = models.Card.objects.all().order_by('-money')
    for inx, t in enumerate(cards):
        worksheet.write(inx+startrow, 1, t.money)
        worksheet.write(inx+startrow, 2, t.name)
    print(('=sum(B%d:B%d)' % (startrow+1,startrow+cards.count())))
    worksheet.write(startrow-1,1,('=sum(B%d:B%d)' % (startrow+1,startrow+cards.count())))
    worksheet.write(startrow-1,2,('%d条' % (cards.count())))


    ticketsInStore = models.Ticket.objects.filter(t_status=1).order_by('-piaomianjiage')
    for inx, t in enumerate(ticketsInStore):
        worksheet.write(inx+startrow, 3, t.piaomianjiage)
        worksheet.write(inx+startrow, 4, t.chupiaohang)
    print(('=sum(D%d:D%d)' % (startrow+1,startrow+ticketsInStore.count())))
    worksheet.write(startrow-1,3,('=sum(D%d:D%d)' % (startrow+1,startrow+ticketsInStore.count())))
    worksheet.write(startrow-1,4,('%d条' % (ticketsInStore.count())))

    borrowOrders = models.Customer.objects.filter(Q(borrow_benjin__gt=0) | Q(borrow_lixi__gt=0)).order_by('-pub_date')
    for inx, order in enumerate(borrowOrders):
        worksheet.write(inx+startrow, 5, order.name)
        worksheet.write(inx+startrow, 6, order.borrow_benjin+order.borrow_lixi)
        # worksheet.write(inx+startrow, 7, order.borrow_lixi)
    sumCont = '=sum(G%d:G%d)' % (startrow+1,startrow+borrowOrders.count())
    print(sumCont)
    worksheet.write(startrow-1,6,sumCont)
    worksheet.write(startrow-1,7,('%d条' % (borrowOrders.count())))

    startrow = 6
    loanOrders = models.Customer.objects.filter(Q(loan_benjin__gt=0) | Q(loan_lixi__gt=0)).order_by('-pub_date')
    sumCont = '=sum(J%d:J%d)' % (startrow + 1, startrow + loanOrders.count())
    print(sumCont)
    worksheet.write(startrow - 1, 9, sumCont)
    worksheet.write(startrow-1,10,('%d条' % (loanOrders.count())))
    for order in loanOrders:
        worksheet.write(startrow, 8, order.name)
        worksheet.write(startrow, 9, order.loan_benjin+order.loan_lixi)
        # worksheet.write(startrow, 10, order.order_date,date_format)
        startrow = startrow + 1



    # worksheet.set_column('A:A', 20)
    # worksheet.set_column('E:E', 20)
    # worksheet.set_column('F:F', 20)
    # worksheet.set_column('J:J', 20)
    # worksheet.write(0, 0, u'购买日期')
    # worksheet.write(0, 1, u'前排票号')
    # worksheet.write(0, 2, u'票号')
    # worksheet.write(0, 3, u'出票行')
    # worksheet.write(0, 4, u'出票日期')
    # worksheet.write(0, 5, u'到期日期')
    # worksheet.write(0, 6, u'票面价格')
    # worksheet.write(0, 7, u'购入价格')
    # worksheet.write(0, 8, u'供应商')
    # worksheet.write(0, 9, u'卖出日期')
    # worksheet.write(0, 10, u'卖出价格')
    # worksheet.write(0, 11, u'买票人')
    # worksheet.write(0, 12, u'利润')
    #
    # tickets = models.Ticket.objects.all()
    # print(tickets)
    # for inx,t in enumerate(tickets):
    #     worksheet.write(inx+1, 0, t.goumairiqi,date_format)
    #     worksheet.write(inx+1, 1, t.qianpaipiaohao)
    #     worksheet.write(inx+1, 2, t.piaohao)
    #     worksheet.write(inx+1, 3, t.chupiaohang)
    #     worksheet.write(inx+1, 4, t.chupiaoriqi,date_format)
    #     worksheet.write(inx+1, 5, t.daoqiriqi,date_format)
    #     worksheet.write(inx+1, 6, t.piaomianjiage)
    #     worksheet.write(inx+1, 7, t.gourujiage)
    #     worksheet.write(inx+1, 8, t.gongyingshang)
    #     worksheet.write(inx+1, 9, t.maichuriqi,date_format)
    #     worksheet.write(inx+1, 10, t.maichujiage)
    #     worksheet.write(inx+1, 11, t.maipiaoren)
    #     worksheet.write(inx+1, 12, t.lirun)
    #
    # worksheet = workbook.add_worksheet(u'日报表1')
    # worksheet.set_column('A:A', 20)
    # worksheet.set_column('E:E', 20)
    # worksheet.set_column('F:F', 20)
    # worksheet.set_column('J:J', 20)
    # worksheet.write(0, 0, u'购买日期')
    # worksheet.write(0, 1, u'前排票号')
    # worksheet.write(0, 2, u'票号')
    # worksheet.write(0, 3, u'出票行')
    # worksheet.write(0, 4, u'出票日期')
    # worksheet.write(0, 5, u'到期日期')
    # worksheet.write(0, 6, u'票面价格')
    # worksheet.write(0, 7, u'购入价格')
    # worksheet.write(0, 8, u'供应商')
    # worksheet.write(0, 9, u'卖出日期')
    # worksheet.write(0, 10, u'卖出价格')
    # worksheet.write(0, 11, u'买票人')
    # worksheet.write(0, 12, u'利润')
    #
    # tickets = models.Ticket.objects.all()
    # print(tickets)
    # for inx,t in enumerate(tickets):
    #     worksheet.write(inx+1, 0, t.goumairiqi,date_format)
    #     worksheet.write(inx+1, 1, t.qianpaipiaohao)
    #     worksheet.write(inx+1, 2, t.piaohao)
    #     worksheet.write(inx+1, 3, t.chupiaohang)
    #     worksheet.write(inx+1, 4, t.chupiaoriqi,date_format)
    #     worksheet.write(inx+1, 5, t.daoqiriqi,date_format)
    #     worksheet.write(inx+1, 6, t.piaomianjiage)
    #     worksheet.write(inx+1, 7, t.gourujiage)
    #     worksheet.write(inx+1, 8, t.gongyingshang)
    #     worksheet.write(inx+1, 9, t.maichuriqi,date_format)
    #     worksheet.write(inx+1, 10, t.maichujiage)
    #     worksheet.write(inx+1, 11, t.maipiaoren)
    #     worksheet.write(inx+1, 12, t.lirun)
    workbook.close()
    pass

def countSuperLoanLixi():
    raw_data = models.SuperLoan.objects.filter(is_payed=False).order_by('-lixi_sum_date')
    countLoanLixi(raw_data)
    pass

def countLoanOrderLixi():
    raw_data = models.Loan_Order.objects.filter(is_payed=False).order_by('-lixi_sum_date')
    countLoanLixi(raw_data)
    pass

def countLoanLixi(raw_data):
    today = datetime.date.today()
    for order in raw_data:
        days = (today - order.lixi_sum_date).days
        if days > 0:
            addLixi = order.benjin_needpay * order.lilv * days / 360
            order.lixi = round(addLixi + order.lixi, 2)
            order.lixi_needpay = round(addLixi + order.lixi_needpay, 2)
            order.lixi_sum_date = today
            order.save()
            try:
                order._meta.get_field('jiedairen')
                customer = order.jiedairen
                if order.order_type == 3:
                    customer.borrow_lixi = customer.borrow_lixi + addLixi
                    customer.save()
                elif order.order_type == 4:
                    customer.loan_lixi = customer.loan_lixi + addLixi
                    customer.save()
            except:
                pass
        pass
    pass

def dailyJob():
    buildDailyReport()
    countLoanOrderLixi()
    countSuperLoanLixi()
    pass

# schedule.every().day.at("00:30").do(dailyJob)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
dailyJob()
