import csv
import datetime
import json
import os
import time
import uuid

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template import loader
# Create your views here.
from django.urls import reverse

from ticket import view_tools, utils
from ticket.forms import TicketForm, CardForm, TicketEditForm, PoolForm, TicketFeeForm, TicketOrderFeeForm, \
    SuperLoanForm, LoanForm, SuperLoanFeeForm, CardTransForm, BestMixForm, LoanPreForm
from ticket.models import Card, Fee, Ticket, Order, StoreFee, Pool, InpoolPercent, TicketsImport, \
    StoreTicketsImport, SuperLoan, Loan_Order, SuperLoanFee, CardTrans, OperLog, Customer, DashBoard, \
    InpoolPercentDetail
from ticket.utils import LogTemp


def ticket_instore(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    storefee = StoreFee()
    storefee.ticket = ticket
    storefee.money = ticket.piaomianjiage
    storefee.storefee_status = 1
    storefee.save()
    pass


def ticket_outstore(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    storefee = StoreFee()
    storefee.ticket = ticket
    storefee.money = 0 - ticket.piaomianjiage
    storefee.storefee_status = 2
    storefee.save()
    pass


def ticket_inpool(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    item = InpoolPercent.objects.last()
    if not item:
        item = InpoolPercent()
        item.inpoolPer = 100
        item.save()
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney + ticket.piaomianjiage * item.inpoolPer / 100
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney + ticket.piaomianjiage * item.inpoolPer / 100
    pool.usedmoney = p.usedmoney
    pool.ticket = ticket
    pool.money = ticket.piaomianjiage
    pool.pool_status = 1
    pool.save()
    pass


def ticket_outpool(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    item = InpoolPercent.objects.last()
    if not item:
        item = InpoolPercent()
        item.inpoolPer = 100
        item.save()
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney - ticket.piaomianjiage * item.inpoolPer / 100
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - ticket.piaomianjiage * item.inpoolPer / 100
    pool.usedmoney = p.usedmoney
    pool.ticket = ticket
    pool.money = 0 - ticket.piaomianjiage
    pool.pool_status = 2
    pool.save()
    pass


def ticket_poolpay(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - ticket.gourujiage
    pool.usedmoney = p.usedmoney + ticket.gourujiage
    pool.ticket = ticket
    pool.money = 0 - ticket.gourujiage
    pool.pool_status = 5
    pool.save()


def card_fee(card_pk, money, name, fee_type):
    card = Card.objects.get(pk=card_pk)
    fee_ins = Fee()
    fee_ins.yinhangka = card
    fee_ins.money = money
    fee_ins.name = name
    fee_ins.fee_type = fee_type
    fee_ins.save()
    card.money = card.money + fee_ins.money
    card.save()
    return fee_ins


# 增加
def ticket_add(request):
    form = TicketForm(request.POST or None)
    context = {
        'form': form,
        'gongyingshang': get_ticketlists('gongyingshang'),
        'chupiaohang': get_ticketlists('chupiaohang'),
    }
    if request.method == 'POST':
        if form.is_valid():
            times = 1
            if form.cleaned_data.get('fenshu') and form.cleaned_data.get('fenshu') > 1:
                times = form.cleaned_data.get('fenshu')
            instance = form.save(commit=False)
            counter = 1
            log = LogTemp()
            while counter <= times:
                counter += 1
                instance.pk = None
                instance.save()
                log.add_detail_ticket(instance.pk)
                if instance.t_status == 1:
                    log.add_kucun(instance.gourujiage)
                elif instance.t_status == 5:
                    log.add_chineipiao(instance.piaomianjiage)
                    bili = utils.get_pool_percent(instance.chupiaohang)
                    edu = round(instance.piaomianjiage * bili / 100 , 2)
                    log.add_keyong(edu)
                    log.add_lirun_yewu(instance.piaomianjiage - edu)
                log.oper_type = 101
                if instance.gouruzijinchi:
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                    instance.save()
                    log.oper_type = 102
                    log.add_keyong(0- instance.gourujiage)
                    log.add_yiyong(instance.gourujiage)
                    pass
            log.save()

            return redirect('ticket_list')
    return render(request, 'ticket/ticket_add.html', context)


def ticket_index(request, pk):
    ticket_ins = get_object_or_404(Ticket, pk=pk)
    form = TicketEditForm(request.POST or None, instance=ticket_ins)

    for m in form.fields:
        form.fields[m].disabled = True
    return render(request, 'ticket/ticket_index.html', locals())


def ticket_fix(request):
    if request.method == 'POST':
        pk = request.POST['t_id']
        t = Ticket.objects.get(pk=pk)
        t.gourujiage = float(request.POST['t_gourujiage'])
        t.save()
        return redirect('ticket_index', pk)
    return redirect('ticket_list')


def get_ticketlists(col):
    gys = Ticket.objects.values(col).annotate(Count('id'))
    t = []
    for g in gys:
        list.insert(t, 0, g[col])
    return t


@login_required
def ticket_list(request):
    context = {
        'gongyingshang': get_ticketlists('gongyingshang'),
        'maipiaoren': get_ticketlists('maipiaoren'),
    }
    if request.method == 'POST':
        log = LogTemp()
        if 'all_tostore' in request.POST.keys():
            print('票据入库')
            ids = request.POST['ids']
            if len(ids) > 0:
                log.oper_type = 103
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if t.t_status == 5:
                        t.t_status = 1
                        t.save()
                        log.add_detail_ticket(t.pk)
                        log.add_kucun(t.gourujiage)
                        log.add_chineipiao(0-t.piaomianjiage)
                        bili = utils.get_pool_percent(t.chupiaohang)
                        edu = round(t.piaomianjiage * bili / 100 , 2)
                        log.add_keyong(0-edu)
                        log.add_feiyong_yewu(t.piaomianjiage - edu)
                log.save()
                context['message'] = u'入库成功'
            pass
        elif 'all_topool' in request.POST.keys():
            print('票据入池')
            ids = request.POST['ids']
            if len(ids) > 0:
                log.oper_type = 104
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if t.t_status == 1:
                        t.t_status = 5
                        t.save()
                        log.add_detail_ticket(t.pk)
                        log.add_kucun(0-t.gourujiage)
                        log.add_chineipiao(t.piaomianjiage)
                        bili = utils.get_pool_percent(t.chupiaohang)
                        edu = round(t.piaomianjiage * bili / 100 , 2)
                        log.add_keyong(edu)
                        log.add_lirun_yewu(t.piaomianjiage - edu)
                log.save()
                context['message'] = u'入池成功'
            pass
    raw_data = Ticket.objects.all().order_by('-goumairiqi')
    print(raw_data)
    list_template = 'ticket/ticket_list.html'

    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def tickets_needfix(request):
    context = {
        'gongyingshang': get_ticketlists('gongyingshang'),
    }
    raw_data = Ticket.objects.filter(pay_status=1, payorder=None, gourujiage=0).order_by('-goumairiqi')
    return utils.get_paged_page(request, raw_data, 'ticket/tickets_needfix.html', context)


def ticket_needselect(request, index):
    if request.method == 'GET':
        if index == 1:
            title = '付款'
            raw_data = Ticket.objects.filter(pay_status=1, payorder=None, gourujiage__gt=0).order_by('-goumairiqi')
        else:
            title = '收款'
            raw_data = Ticket.objects.filter(sell_status=3, sellorder=None).order_by('-goumairiqi')
        list_template = 'ticket/ticket_toselect.html'
        context = {
            'index': index,
            'title': title,
            'gongyingshang': get_ticketlists('gongyingshang'),
        }
        print(context)
        # 跳转到相应页面，并将值传递过去
        return getPagedPage(request, raw_data, list_template, context)
    elif request.method == 'POST':
        feeform = TicketFeeForm()
        index = request.POST['index']
        ids = request.POST['ids']
        selected_num = request.POST['selected_num']
        selected_piaomian = request.POST['selected_piaomian']
        selected_real = request.POST['selected_real']
        raw_data = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        prices = set([])
        maipiaoren = []
        if index == '1':
            title = '付款'
            list_template = 'ticket/ticket_topay.html'
        else:
            title = '收款'
            list_template = 'ticket/ticket_tocollect.html'
            maipiaoren = get_ticketlists('maipiaoren')
            for t in raw_data:
                prices.add(str(t.piaomianjiage))
        # 建立context字典，将值传递到相应页面
        context = {
            'data': raw_data,
            'maipiaoren': maipiaoren,
            'prices': prices,
            'index': index,
            'ids': ids,
            'title': title,
            'feeform': feeform,
            'selected_num': selected_num,
            'selected_piaomian': selected_piaomian,
            'selected_real': selected_real,
        }
        print(context)
        # 跳转到相应页面，并将值传递过去
        return render(request, list_template, context)


def ticket_needpay(request):
    return ticket_needselect(request, 1)


def ticket_needcollect(request):
    return ticket_needselect(request, 3)


def ticket_createorder(request):
    if request.method == 'POST':
        order = Order()
        order.order_type = int(request.POST['ordertype'])
        order.save()
        log = LogTemp()
        fees = json.loads(request.POST['fees'])
        for fee in fees:
            f = Fee()
            f.order = order
            f.fee_type = order.order_type
            f.name = fee['name']
            f.money = float(fee['money'])
            f.yinhangka = Card.objects.get(pk=(fee['cardid']))
            f.save()
            order.fee_sum = order.fee_sum + f.money
            order.fee_count = order.fee_count + 1

        ids = request.POST['ids']
        if order.order_type == 1:
            Ticket.objects.filter(id__in=ids.split(',')).update(pay_status=2, payorder=order, paytime=order.pub_date)
            log.oper_type = 201
            log.adddetail(6, order.pk)
        elif order.order_type == 2:
            Ticket.objects.filter(id__in=ids.split(',')).update(t_status=3, sell_status=4, sellorder=order,
                                                                selltime=order.pub_date,
                                                                maipiaoren=request.POST['maipiaoren'])
            log.oper_type = 202
            log.adddetail(7, order.pk)

        tickets = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        for t in tickets:
            log.adddetail(1, t.pk)
            order.ticket_count = order.ticket_count + 1
            order.ticket_sum = order.ticket_sum + t.piaomianjiage
            if order.order_type == 1:
                order.money = order.money + t.gourujiage
            elif order.order_type == 2:
                t.maichujiage = float(request.POST['maichujiage' + str(t.piaomianjiage)])
                t.save()
                order.money = order.money + int(request.POST['maichujiage' + str(t.piaomianjiage)])
            if t.gourujiage > 0 and t.maichujiage > 0:
                t.lirun = t.maichujiage - t.gourujiage
                t.save()
        order.total_sum = order.money + order.fee_sum
        order.payfee_sum = 0
        order.needpay_sum = order.total_sum - order.payfee_sum
        order.save()
        log.save()
        if order.order_type == 1:
            return redirect('ticket_payorder', pk=order.id)
        elif order.order_type == 2:
            return redirect('ticket_sellorder', pk=order.id)

        # todo
    return redirect('ticket_payorder', pk=order.id)


def ticket_orderlist(request, index):
    # 从根据不同的请求，来获取相应的数据,并跳转至相应页面
    list_template = 'ticket/ticket_orders.html'
    raw_data = Order.objects.filter(order_type=index).order_by('-pub_date')
    context = {
        'index': index,
    }
    return getPagedPage(request, raw_data, list_template, context)


def ticket_payorders(request):
    return ticket_orderlist(request, 1)


def ticket_sellorders(request):
    return ticket_orderlist(request, 2)


def ticket_payorder(request, pk):
    order_ins = get_object_or_404(Order, pk=pk)
    order = Order.objects.get(pk=pk)
    ticket_data = Ticket.objects.filter(payorder=pk).order_by('-goumairiqi')
    fee_data = Fee.objects.filter(order=pk, fee_type=1).order_by('-pub_date')
    payfee_data = Fee.objects.filter(Q(order=pk) & (Q(fee_type=3) | Q(fee_type=5) | Q(fee_type=7))).order_by(
        '-pub_date')
    list_template = 'ticket/ticket_payorder.html'
    feeform = TicketOrderFeeForm(request.POST or None)
    # feeform.fields['money'].max_value = needpay_sum
    if request.method == 'POST':
        if feeform.is_valid():
            if feeform.cleaned_data.get('money') > order.needpay_sum:
                message = u'付款金额不能大于待支付金额'
            else:
                log = LogTemp()
                log.oper_type = 203
                cardmoneyadd = False
                instance = feeform.save(commit=False)
                instance.order = order
                if feeform.cleaned_data.get('isOrderFee'):
                    if feeform.cleaned_data.get('fee_status') == '1':  # 收入
                        instance.fee_type = 7
                    elif feeform.cleaned_data.get('fee_status') == '2':  # 支出
                        instance.fee_type = 5
                        instance.money = -1 * instance.money
                else:
                    order.payfee_count = order.payfee_count + 1
                    order.payfee_sum = order.payfee_sum + instance.money
                    order.needpay_sum = order.total_sum - order.payfee_sum
                    order.save()
                    instance.fee_type = 3
                    instance.money = -1 * instance.money
                instance.save()
                instance.yinhangka.money = instance.yinhangka.money + instance.money
                instance.yinhangka.save()
                log.adddetail(6, pk)
                log.adddetail(2, instance.yinhangka.pk)
                log.addxianjin(instance.money)
                log.save()

                redirect('ticket_payorder', pk=pk)
    return render(request, list_template, locals())


def ticket_sellorder(request, pk):
    order_ins = get_object_or_404(Order, pk=pk)
    order = Order.objects.get(pk=pk)
    ticket_data = Ticket.objects.filter(sellorder=pk).order_by('-goumairiqi')
    fee_data = Fee.objects.filter(order=pk, fee_type=2).order_by('-pub_date')
    payfee_data = Fee.objects.filter(Q(order=pk) & (Q(fee_type=4) | Q(fee_type=6) | Q(fee_type=8))).order_by(
        '-pub_date')
    list_template = 'ticket/ticket_sellorder.html'
    feeform = TicketOrderFeeForm(request.POST or None)
    if request.method == 'POST':
        if feeform.is_valid():
            if feeform.cleaned_data.get('money') > order.needpay_sum:
                message = u'收款金额不能大于待收取金额'
            else:
                log = LogTemp()
                log.oper_type = 204
                instance = feeform.save(commit=False)
                instance.order = order
                if feeform.cleaned_data.get('isOrderFee'):
                    if feeform.cleaned_data.get('fee_status') == '1':  # 收入
                        instance.fee_type = 8
                    elif feeform.cleaned_data.get('fee_status') == '2':  # 支出
                        instance.fee_type = 6
                        instance.money = -1 * instance.money
                else:
                    instance.fee_type = 4
                    order.payfee_count = order.payfee_count + 1
                    order.payfee_sum = order.payfee_sum + instance.money
                    order.needpay_sum = order.total_sum - order.payfee_sum
                    order.save()
                instance.save()
                instance.yinhangka.money = instance.yinhangka.money + instance.money
                instance.yinhangka.save()
                log.adddetail(7, pk)
                log.adddetail(2, instance.yinhangka.pk)
                log.addxianjin(instance.money)
                log.save()

                redirect('ticket_sellorder', pk=pk)
    return render(request, list_template, locals())


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

