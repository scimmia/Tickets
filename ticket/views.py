import csv
import datetime
import os
import uuid

from django.db.models import Sum, Count, Q
from django.shortcuts import redirect

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from ticket import utils
from ticket.models import Ticket, TicketsImport, StoreTicketsImport, SuperLoan, Loan_Order, DashBoard


def dashboard(request):
    ts = Ticket.objects.values('t_status', 't_type').annotate(t_count=Count('id'), sum_money=Sum('piaomianjiage'))
    kudianc = 0
    kudians = 0
    kuzhic = 0
    kuzhis = 0
    chidianc = 0
    chidians = 0
    chizhic = 0
    chizhis = 0
    for t in ts:
        if t['t_status'] == 1:
            if t['t_type'] == 1:
                kuzhic = t['t_count']
                kuzhis = round(t['sum_money'], 2)
                pass
            elif t['t_type'] == 2:
                kudianc = t['t_count']
                kudians = round(t['sum_money'], 2)
                pass
        elif t['t_status'] == 5:
            if t['t_type'] == 1:
                chizhic = t['t_count']
                chizhis = round(t['sum_money'], 2)
                pass
            elif t['t_type'] == 2:
                chidianc = t['t_count']
                chidians = round(t['sum_money'], 2)
                pass
        pass
    kuc = kudianc + kuzhic
    kus = round(kudians + kuzhis, 2)
    chic = chidianc + chizhic
    chis = round(chidians + chizhis, 2)
    allc = kuc + chic
    alls = round(kus + chis, 2)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    threeday = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    # count_t = Ticket.objects.filter(Q(t_status=5)&Q(daoqiriqi__gt=today)).count()
    ts = Ticket.objects.filter(Q(t_status=5) & Q(daoqiriqi__lte=today)).values('t_status').annotate(t_count=Count('id'),
                                                                                                    sum_money=Sum(
                                                                                                        'piaomianjiage'))
    daoqizaichi_count = 0
    daoqizaichi_sum = 0
    for t in ts:
        if t['t_status'] == 5:
            daoqizaichi_count = t['t_count']
            daoqizaichi_sum = round(t['sum_money'], 2)
    ts = Ticket.objects.filter(Q(t_status=1) & Q(daoqiriqi__lte=threeday)).values('t_status').annotate(
        t_count=Count('id'), sum_money=Sum('piaomianjiage'))
    daoqikucun_count = 0
    daoqikucun_sum = 0
    for t in ts:
        if t['t_status'] == 1:
            daoqikucun_count = t['t_count']
            daoqikucun_sum = round(t['sum_money'], 2)
    # ts = SuperLoan.objects.filter(Q(needpay_sum__gt=0)|Q(needpay_lixi__gt=0)).annotate(t_count = Count('id'),sum_money=Sum('needpay_sum'),sum_lixi=Sum('needpay_lixi'))

    superLoans = SuperLoan.objects.filter(is_payed=False,lixi_end_date__lte=threeday)
    loan_count = 0
    loan_sum = 0
    for superLoan in superLoans:
        loan_count += 1
        loan_sum = loan_sum + superLoan.benjin_needpay + superLoan.lixi_needpay
    # payfee_data = Fee.objects.filter(Q(order=pk)&(Q(fee_type=3)|Q(fee_type=5)|Q(fee_type=7))).order_by('-pub_date')

    loanOrders = Loan_Order.objects.filter(is_payed=False)
    daishou_count = 0
    daishou_sum = 0
    daifu_count = 0
    daifu_sum = 0
    for loanOrder in loanOrders:
        if loanOrder.order_type == 4:
            daifu_count += 1
            daifu_sum += loanOrder.benjin_needpay + loanOrder.lixi_needpay
        if loanOrder.order_type == 3:
            daishou_count += 1
            daishou_sum += loanOrder.benjin_needpay + loanOrder.lixi_needpay

    dashs = DashBoard.objects.filter().order_by('-day')
    dashs, page_range, count, page_nums = utils.pagination(request, dashs)

    return render(request, 'ticket/dashboard.html', locals())


# 用户登陆
def login(request):
    template_response = views.login(request, extra_context={'next': '/t/dashboard/'})
    return template_response


# 用户退出
def logout(request):
    # logout_then_login表示退出即跳转至登陆页面，login_url为登陆页面的url地址
    template_response = views.logout_then_login(request, login_url='/t/login/')
    return template_response


# 密码更改
@login_required
def password_change(request):
    # post_change_redirect表示密码成功修改后将跳转的页面.
    template_response = views.password_change(request, post_change_redirect='/index/')
    return template_response


def ticket_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = TicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            csv_reader = csv.reader(open(path + 'tmp.csv', 'r', newline=''))
            print(datetime.datetime.now())
            ticketsImports = []
            for row in csv_reader:
                a = len(row)
                if len(row) == 14:
                    if row[5].startswith('2'):
                        m = TicketsImport()
                        m.stamp = stamp
                        m.piaohao = row[0]
                        m.chupiaoren = row[1]
                        m.shoukuanren = row[2]
                        m.piaomianjiage = float(row[3].replace(',', ''))
                        m.piaomianlixi = row[4]
                        m.chupiaoriqi = row[5].replace(' ', '').replace('\t', '')
                        m.daoqiriqi = row[6].replace(' ', '').replace('\t', '')
                        m.leixing = row[7]
                        m.zhuangtai = row[8]
                        m.chupiaohang = row[9]
                        m.chupiaohangb = row[10]
                        m.chengduiren = row[11]
                        m.shoupiaoren = row[12]
                        m.shoupiaohang = row[13]
                        ticketsImports.append(m)
            TicketsImport.objects.bulk_create(ticketsImports)
            print(datetime.datetime.now())

            return redirect('%s?stamp=%s' % (reverse('ticket_import'), stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            TicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = TicketsImport.objects.filter(stamp=stamp)
            print(datetime.datetime.now())
            tickets = []
            for item in items:
                m = Ticket()
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.piaomianjiage
                m.gongyingshang = item.chupiaoren
                tickets.append(m)
                pass
            Ticket.objects.bulk_create(tickets)
            print(datetime.datetime.now())

            return redirect('ticket_list')
            pass
        # return redirect('ticket_import',)

    # 如果是通过GET方法请求数据，返回一个空的表单
    # else:
    # form = NameForm()
    # context['forma'] = form
    return render(request, 'ticket/ticket_import.html', locals())


def flow_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = StoreTicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            with open(path + 'tmp.csv', mode='r', encoding='utf-8', newline='') as f:
                # 此处读取到的数据是将每行数据当做列表返回的
                reader = csv.reader(f)
                for row in reader:
                    # 此时输出的是一行行的列表
                    # print(row)
                    a = len(row)
                    if len(row) == 10:
                        if row[0].startswith('2'):
                            m = StoreTicketsImport()
                            m.stamp = stamp
                            m.qianpaipiaohao = row[1]
                            m.piaohao = row[2]
                            m.maipiaoriqi = row[0].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.chupiaoren = row[9]
                            m.piaomianjiage = float(row[6].replace(',', ''))
                            if row[7].isdigit():
                                m.piaomianlixi = float(row[7])
                            m.chupiaoriqi = row[4].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.daoqiriqi = row[5].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.leixing = '流水表'
                            m.chupiaohang = row[3]
                            m.save()
                            print(row)

            return redirect('%s?stamp=%s' % (reverse('flow_import'), stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            StoreTicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = StoreTicketsImport.objects.filter(stamp=stamp)
            for item in items:
                m = Ticket()
                m.qianpaipiaohao = item.qianpaipiaohao
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.piaomianjiage - item.piaomianlixi
                m.pay_status = 2
                m.gongyingshang = item.chupiaoren
                m.save()
                m.goumairiqi = item.maipiaoriqi
                m.save()
                pass

            return redirect('ticket_list')
            pass
        # return redirect('ticket_import',)

    # 如果是通过GET方法请求数据，返回一个空的表单
    # else:
    # form = NameForm()
    # context['forma'] = form
    return render(request, 'ticket/ticket_import.html', locals())


def pool_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = StoreTicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            with open(path + 'tmp.csv', mode='r', encoding='utf-8', newline='') as f:
                # 此处读取到的数据是将每行数据当做列表返回的
                reader = csv.reader(f)
                for row in reader:
                    # 此时输出的是一行行的列表
                    # print(row)
                    a = len(row)
                    if len(row) == 10:
                        if row[0].startswith('2'):
                            m = StoreTicketsImport()
                            m.stamp = stamp
                            m.qianpaipiaohao = row[1]
                            m.piaohao = row[2]
                            m.maipiaoriqi = row[0].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.chupiaoren = row[9]
                            m.piaomianjiage = float(row[6].replace(',', ''))
                            m.piaomianlixi = m.piaomianjiage - float(row[8].replace(',', ''))
                            m.chupiaoriqi = row[4].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.daoqiriqi = row[5].replace(' ', '').replace('\t', '').replace('/', '-')
                            m.leixing = '流水表'
                            m.chupiaohang = row[3]
                            m.save()
                            print(row)

            return redirect('%s?stamp=%s' % (reverse('pool_import'), stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            StoreTicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = StoreTicketsImport.objects.filter(stamp=stamp)
            for item in items:
                m = Ticket()
                m.qianpaipiaohao = item.qianpaipiaohao
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.piaomianjiage - item.piaomianlixi
                m.pay_status = 2
                m.t_status = 5
                m.gongyingshang = item.chupiaoren
                m.save()
                m.goumairiqi = item.maipiaoriqi
                m.save()
                # ticket_inpool(m.pk)
                pass

            return redirect('ticket_list')
            pass
        # return redirect('ticket_import',)

    # 如果是通过GET方法请求数据，返回一个空的表单
    # else:
    # form = NameForm()
    # context['forma'] = form
    return render(request, 'ticket/ticket_import.html', locals())


def handle_upload_file(file):
    path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + 'tmp.csv', 'wb+')as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    csv_reader = csv.reader(open(path + 'tmp.csv', 'r', newline=''))
    res = []
    for row in csv_reader:
        a = len(row)
        if len(row) == 14:
            if row[5].startswith('2'):
                m = Ticket()
                m.qianpaipiaohao = row[0]
                m.piaohao = row[0]
                m.chupiaohang = row[9]
                m.chupiaoriqi = row[5]
                m.daoqiriqi = row[6]
                m.piaomianjiage = row[3]
                res.append(m)
                print(row)

            pass
    return res
