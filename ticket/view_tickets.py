import csv
import datetime
import os
import uuid

from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from ticket import utils
from ticket.forms import TicketForm, TicketEditForm, TicketOrderFeeForm, MoneyWithCardForm
from ticket.models import Card, Fee, Ticket, Order, StoreFee, Pool, InpoolPercent, TicketsImport, \
    StoreTicketsImport, FeeDetail
from ticket.utils import LogTemp


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
                    edu = round(instance.piaomianjiage * bili / 100, 2)
                    log.add_keyong(edu)
                    log.add_lirun_yewu(instance.piaomianjiage - edu)
                log.oper_type = 101
                if instance.gouruzijinchi and instance.t_status != 2:
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                    instance.save()
                    log.oper_type = 102
                    log.add_keyong(0 - instance.gourujiage)
                    log.add_yiyong(instance.gourujiage)
                    pass
            log.save()

            return redirect('ticket_list')
    return render(request, 'ticket/ticket_add.html', context)


# 编辑查看
def ticket_index(request, pk):
    ticket_ins = get_object_or_404(Ticket, pk=pk)
    context = {
        'ticket_ins': ticket_ins,
    }
    if ticket_ins.t_status != 2:
        template_name = 'ticket/ticket_index.html'
        form = TicketEditForm(request.POST or None, instance=ticket_ins)
        for m in form.fields:
            form.fields[m].disabled = True
    else:
        template_name = 'ticket/ticket_edit.html'
        form = TicketForm(request.POST or None, instance=ticket_ins)
        context['gongyingshang'] = get_ticketlists('gongyingshang')
        context['chupiaohang'] = get_ticketlists('chupiaohang')
        if request.method == 'POST':
            if form.is_valid():
                instance = form.save(commit=False)
                log = LogTemp()
                instance.save()
                log.add_detail_ticket(instance.pk)
                if instance.t_status == 1:
                    log.add_kucun(instance.gourujiage)
                elif instance.t_status == 5:
                    log.add_chineipiao(instance.piaomianjiage)
                    bili = utils.get_pool_percent(instance.chupiaohang)
                    edu = round(instance.piaomianjiage * bili / 100, 2)
                    log.add_keyong(edu)
                    log.add_lirun_yewu(instance.piaomianjiage - edu)
                log.oper_type = 107
                if instance.gouruzijinchi and instance.t_status != 2:
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                    instance.save()
                    log.oper_type = 108
                    log.add_keyong(0 - instance.gourujiage)
                    log.add_yiyong(instance.gourujiage)
                    pass
                log.save()
                context['message'] = u'保存成功'
                if instance.t_status != 2:
                    return redirect('ticket_index', pk)
    context['form'] = form
    return render(request, template_name, context)


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
                        log.add_chineipiao(0 - t.piaomianjiage)
                        bili = utils.get_pool_percent(t.chupiaohang)
                        edu = round(t.piaomianjiage * bili / 100, 2)
                        log.add_keyong(0 - edu)
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
                        log.add_kucun(0 - t.gourujiage)
                        log.add_chineipiao(t.piaomianjiage)
                        bili = utils.get_pool_percent(t.chupiaohang)
                        edu = round(t.piaomianjiage * bili / 100, 2)
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
    raw_data = Ticket.objects.filter(t_status=2).order_by('-goumairiqi')
    return utils.get_paged_page(request, raw_data, 'ticket/tickets_needfix.html', context)


def ticket_needselect(request, index):
    if request.method == 'GET':
        if index == 1:
            raw_data = Ticket.objects.filter(~Q(t_status=2), pay_status=1, payorder=None, gourujiage__gt=0).order_by(
                '-goumairiqi')
        else:
            raw_data = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None).order_by('-goumairiqi')
        list_template = 'ticket/ticket_toselect.html'
        context = {
            'index': index,
            'gongyingshang': get_ticketlists('gongyingshang'),
        }
        return utils.get_paged_page(request, raw_data, list_template, context)
    elif request.method == 'POST':
        ids = request.POST['ids']
        selected_num = request.POST['selected_num']
        selected_piaomian = request.POST['selected_piaomian']
        selected_real = request.POST['selected_real']
        raw_data = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')

        context = {
            'index': index,
            'data': raw_data,
            'ids': ids,
            'selected_num': selected_num,
            'selected_piaomian': selected_piaomian,
            'selected_real': selected_real,
        }
        if index == 2:
            prices = set([])
            for t in raw_data:
                prices.add(str(t.piaomianjiage))
            context['prices'] = prices
        return render(request, 'ticket/ticket_order_preview.html', context)


def ticket_needpay(request):
    return ticket_needselect(request, 1)


def ticket_needcollect(request):
    return ticket_needselect(request, 2)


def ticket_createorder(request):
    if request.method == 'POST':
        order = Order()
        order.order_type = int(request.POST['ordertype'])
        order.save()
        log = LogTemp()

        ids = request.POST['ids']
        if order.order_type == 1:
            Ticket.objects.filter(id__in=ids.split(',')).update(pay_status=2, payorder=order, paytime=order.pub_date)
            log.oper_type = 201
            log.add_detail_ticketorder(order.pk)
        elif order.order_type == 2:
            Ticket.objects.filter(id__in=ids.split(',')).update(t_status=3, sell_status=4, sellorder=order,
                                                                selltime=order.pub_date,
                                                                maipiaoren=request.POST['maipiaoren'])
            log.oper_type = 202
            log.add_detail_ticketorder(order.pk)

        tickets = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        log.add_detail_ticketorder(order.pk)
        for t in tickets:
            log.add_detail_ticket(t.pk)
            order.ticket_count += 1
            order.ticket_sum += t.piaomianjiage
            if order.order_type == 1:
                order.money += t.gourujiage
                log.add_need_pay(t.gourujiage)
            elif order.order_type == 2:
                t.maichujiage = round(float(request.POST['maichujiage' + str(t.piaomianjiage)]), 2)
                t.lirun = t.maichujiage - t.gourujiage
                t.save()
                order.money += t.maichujiage
                log.add_need_collect(t.maichujiage)
                log.add_lirun_yewu(t.lirun)
        order.total_sum = order.money
        order.needpay_sum = order.total_sum - order.payfee_sum
        order.save()
        log.save()
        return redirect('ticket_order', pk=order.id)


def ticket_orderlist(request, index):
    list_template = 'ticket/ticket_orders.html'
    raw_data = Order.objects.filter(order_type=index).order_by('-pub_date')
    context = {
        'index': index,
    }
    return utils.get_paged_page(request, raw_data, list_template, context)


def ticket_payorders(request):
    return ticket_orderlist(request, 1)


def ticket_sellorders(request):
    return ticket_orderlist(request, 2)


def ticket_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.order_type == 1:
        ticket_data = Ticket.objects.filter(payorder=pk).order_by('-goumairiqi')
    elif order.order_type == 2:
        ticket_data = Ticket.objects.filter(sellorder=pk).order_by('-goumairiqi')
    list_template = 'ticket/ticket_order.html'
    feeform = MoneyWithCardForm(request.POST or None)
    context = {
        'order': order,
        'ticket_data': ticket_data,
        'feeform': feeform,
    }
    if request.method == 'POST':
        if feeform.is_valid():
            instance = feeform.save(commit=False)
            money = instance.money
            card = instance.card
            log = LogTemp()
            log.add_detail_ticketorder(pk)
            log.add_detail_card(card.pk)
            if order.order_type == 1:
                if money > order.needpay_sum:
                    context['message'] = u'付款金额不能大于待支付金额'
                else:
                    log.oper_type = 203
                    order.payfee_count += 1
                    order.payfee_sum += money
                    order.needpay_sum -= money
                    order.save()
                    log.add_xianjin(0 - money)
                    log.add_need_pay(0 - money)
                    log.save()
                    utils.create_card_fee(card, 0 - money, log)
                    utils.create_ticket_order_fee(order, 0 - money, log)
                    context['message'] = u'付款成功'
            elif order.order_type == 2:
                if money > order.needpay_sum:
                    context['message'] = u'收款金额不能大于待收取金额'
                else:
                    log.oper_type = 204
                    order.payfee_count += 1
                    order.payfee_sum += money
                    order.needpay_sum -= money
                    order.save()
                    log.add_xianjin(money)
                    log.add_need_collect(0 - money)
                    log.save()
                    utils.create_card_fee(card, money, log)
                    utils.create_ticket_order_fee(order, money, log)
                    context['message'] = u'收款成功'
    fee_data = FeeDetail.objects.filter(fee_detail_type=2, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, list_template, context)


def ticket_import(request):
    context = {}
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
            log = LogTemp()
            log.oper_type = 106
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
            log.save()

            return redirect('ticket_list')
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
