import csv
import datetime
import os
import uuid
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from ticket import utils, view_loan
from ticket.forms import TicketForm, TicketEditForm, MoneyForm, TicketTransForm
from ticket.models import Card, Ticket, Order, TicketsImport, StoreTicketsImport, FeeDetail, OperLog, Pool


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
            log, detail = utils.create_log()
            log.oper_type = 101
            while counter <= times:
                counter += 1
                instance.pk = None
                instance.save()
                detail.add_detail_ticket(instance.pk)
                if instance.gouruzijinchi and instance.t_status != 2:
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                    instance.save()
            if instance.t_status == 1:
                log.kucun += Decimal(instance.gourujiage * times)
            elif instance.t_status == 5:
                jiage = instance.piaomianjiage * times
                detail.add_detail_pool(instance.pool_in.pk)
                bili = utils.get_pool_percent(instance.pool_in, instance.chupiaohang)
                edu = round(jiage * bili / 100, 2)
                feiyong = jiage - edu
                log.edu_chineipiao += Decimal(jiage)
                log.edu_keyong += Decimal(edu)
                log.feiyong_yewu += Decimal(feiyong)
                instance.pool_in.edu_keyong += Decimal(edu)
                instance.pool_in.edu_chineipiao += Decimal(jiage)
                instance.pool_in.save()
                utils.create_fee_detail(jiage, 9, instance.pool_in.pk, log)
            if instance.gouruzijinchi and instance.t_status != 2:
                log.oper_type = 102
                jiage = instance.piaomianjiage * times
                detail.add_detail_pool(instance.pool_buy.pk)
                log.edu_keyong -= Decimal(jiage)
                log.edu_yiyong += Decimal(jiage)
                instance.pool_buy.edu_keyong -= Decimal(jiage)
                instance.pool_buy.edu_yiyong += Decimal(jiage)
                instance.pool_buy.save()
                utils.create_fee_detail(jiage, 9, instance.pool_buy.pk, log)
            utils.save_log(log, detail)
            context['message'] = u'保存成功'
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
                instance.save()
                log, detail = utils.create_log()
                log.oper_type = 107
                jiage = instance.gourujiage
                detail.add_detail_ticket(instance.pk)
                if instance.t_status == 1:
                    log.kucun += Decimal(jiage)
                elif instance.t_status == 5:
                    detail.add_detail_pool(instance.pool_in.pk)
                    bili = utils.get_pool_percent(instance.pool_in, instance.chupiaohang)
                    edu = round(jiage * bili / 100, 2)
                    feiyong = jiage - edu
                    log.edu_chineipiao += Decimal(jiage)
                    log.edu_keyong += Decimal(edu)
                    log.lirun_yewu += Decimal(feiyong)
                    instance.pool_in.edu_keyong += Decimal(edu)
                    instance.pool_in.edu_chineipiao += Decimal(jiage)
                    instance.pool_in.save()
                    utils.create_fee_detail(jiage, 9, instance.pool_in.pk, log)
                if instance.gouruzijinchi and instance.t_status != 2:
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                    instance.save()
                    log.oper_type = 108
                    detail.add_detail_pool(instance.pool_buy.pk)
                    log.edu_keyong -= Decimal(jiage)
                    log.edu_yiyong += Decimal(jiage)
                    instance.pool_buy.edu_keyong -= Decimal(edu)
                    instance.pool_buy.edu_yiyong += Decimal(jiage)
                    instance.pool_buy.save()
                    utils.create_fee_detail(jiage, 9, instance.pool_buy.pk, log)
                utils.save_log(log, detail)
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


def ticket_list(request):
    pools = Pool.objects.all()
    form = TicketTransForm(request.POST or None)
    context = {
        'gongyingshang': get_ticketlists('gongyingshang'),
        'maipiaoren': get_ticketlists('maipiaoren'),
        'pools': pools,
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            ids = request.POST['ids']
            if len(ids) > 0:
                log, detail = utils.create_log()
                p_status = form.cleaned_data.get('p_status')
                if p_status == '1':
                    # '票据入库'
                    tickets = Ticket.objects.filter(t_status=5, id__in=ids.split(','))
                    if len(tickets) > 0:
                        log.oper_type = 103
                        for t in tickets:
                            pool = t.pool_in
                            detail.add_detail_ticket(t.pk)
                            detail.add_detail_pool(pool.pk)
                            t.t_status = 1
                            t.pool_in = None
                            t.save()
                            log.kucun += Decimal(t.gourujiage)
                            jiage = t.piaomianjiage
                            bili = utils.get_pool_percent(pool, t.chupiaohang)
                            edu = round(jiage * bili / 100, 2)
                            log.edu_chineipiao -= Decimal(jiage)
                            log.edu_keyong -= Decimal(edu)
                            log.feiyong_yewu += Decimal(jiage - edu)
                            pool.edu_keyong -= Decimal(edu)
                            pool.edu_chineipiao -= Decimal(jiage)
                            pool.save()
                        utils.save_log(log, detail)
                        context['message'] = u'入库成功'
                    else:
                        context['errormsg'] = u'请选择至少一张在池票据'
                    pass
                elif p_status == '2':
                    # '票据入池'
                    target_pool = form.cleaned_data.get('pool')
                    tickets = Ticket.objects.filter(
                        Q(id__in=ids.split(',')) & (Q(t_status=1) | (Q(t_status=5) & (~Q(pool_in=target_pool)))))
                    if len(tickets) > 0:
                        log.oper_type = 104
                        detail.add_detail_pool(target_pool.pk)
                        for t in tickets:
                            detail.add_detail_ticket(t.pk)
                            if t.t_status == 1:
                                # 从库到池
                                pool = target_pool
                                t.t_status = 5
                                t.pool_in = target_pool
                                t.save()
                                log.kucun -= Decimal(t.gourujiage)
                                jiage = t.piaomianjiage
                                bili = utils.get_pool_percent(pool, t.chupiaohang)
                                edu = round(jiage * bili / 100, 2)
                                log.edu_chineipiao += Decimal(jiage)
                                log.edu_keyong += Decimal(edu)
                                log.feiyong_yewu += Decimal(jiage - edu)
                                pool.edu_keyong += Decimal(edu)
                                pool.edu_chineipiao += Decimal(jiage)
                                pool.save()
                            elif t.t_status == 5:
                                # 从池到池
                                # 旧池减少
                                pool = t.pool_in
                                detail.add_detail_pool(pool.pk)
                                t.pool_in = target_pool
                                t.save()
                                jiage = t.piaomianjiage
                                bili = utils.get_pool_percent(pool, t.chupiaohang)
                                edu = round(jiage * bili / 100, 2)
                                log.edu_chineipiao -= Decimal(jiage)
                                log.edu_keyong -= Decimal(edu)
                                log.feiyong_yewu += Decimal(jiage - edu)
                                pool.edu_keyong -= Decimal(edu)
                                pool.edu_chineipiao -= Decimal(jiage)
                                pool.save()
                                # 新池增加
                                pool = target_pool
                                jiage = t.piaomianjiage
                                bili = utils.get_pool_percent(pool, t.chupiaohang)
                                edu = round(jiage * bili / 100, 2)
                                log.edu_chineipiao += Decimal(jiage)
                                log.edu_keyong += Decimal(edu)
                                log.feiyong_yewu += Decimal(jiage - edu)
                                pool.edu_keyong += Decimal(edu)
                                pool.edu_chineipiao += Decimal(jiage)
                                pool.save()
                        utils.save_log(log, detail)
                        context['message'] = u'入池成功'
                    else:
                        context['errormsg'] = u'请选择至少一张非该库票据'
                    pass
            else:
                context['errormsg'] = u'请选择至少一张票据'
    raw_data = Ticket.objects.all().order_by('-goumairiqi')
    list_template = 'ticket/ticket_list.html'
    return utils.get_paged_page(request, raw_data, list_template, context)


def tickets_needfix(request):
    context = {
        'gongyingshang': get_ticketlists('gongyingshang'),
    }
    raw_data = Ticket.objects.filter(t_status=2).order_by('-goumairiqi')
    return utils.get_paged_page(request, raw_data, 'ticket/tickets_needfix.html', context)


def ticket_needselect(request, index):
    context = {
        'index': index,
        'gongyingshang': get_ticketlists('gongyingshang'),
    }
    if request.method == 'POST':
        ids = request.POST['ids']
        selected_num = request.POST['selected_num']
        selected_piaomian = request.POST['selected_piaomian']
        selected_real = request.POST['selected_real']
        if int(selected_num) > 0:
            raw_data = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
            context = {
                'index': index,
                'data': raw_data,
                'ids': ids,
                'selected_num': selected_num,
                'selected_piaomian': selected_piaomian,
                'selected_real': selected_real,
            }
            if index == 1:
                context['maipiaoren'] = raw_data[0].gongyingshang
            elif index == 2:
                prices = set([])
                for t in raw_data:
                    prices.add(str(t.piaomianjiage))
                context['prices'] = prices
            return render(request, 'ticket/ticket_order_preview.html', context)
        else:
            context['message'] = u'请选择至少一张票据'
    if index == 1:
        raw_data = Ticket.objects.filter(~Q(t_status=2), pay_status=1, payorder=None, gourujiage__gt=0).order_by(
            '-goumairiqi')
    else:
        raw_data = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None).order_by('-goumairiqi')
    list_template = 'ticket/ticket_toselect.html'
    return utils.get_paged_page(request, raw_data, list_template, context)


def ticket_needpay(request):
    return ticket_needselect(request, 1)


def ticket_needcollect(request):
    return ticket_needselect(request, 2)


def ticket_createorder(request):
    if request.method == 'POST':
        order = Order()
        order.order_type = int(request.POST['ordertype'])
        order.customer = view_loan.get_customer_by_name(request.POST['maipiaoren'])
        order.save()
        log, detail = utils.create_log()

        ids = request.POST['ids']
        if order.order_type == 1:
            Ticket.objects.filter(id__in=ids.split(',')).update(pay_status=2, payorder=order, paytime=order.pub_date)
            log.oper_type = 201
        elif order.order_type == 2:
            log.oper_type = 202
        detail.add_detail_ticketorder(order.pk)
        tickets = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        for t in tickets:
            detail.add_detail_ticket(t.pk)
            order.ticket_count += 1
            order.ticket_sum += t.piaomianjiage
            if order.order_type == 1:
                order.money += t.gourujiage
                log.need_pay += Decimal(t.gourujiage)
            elif order.order_type == 2:
                if t.t_status == 1:
                    # 在库
                    log.kucun -= Decimal(t.gourujiage)
                elif t.t_status == 5 or t.t_status == 7:
                    # 在池
                    pool = t.pool_in
                    detail.add_detail_pool(pool.pk)
                    t.pool_in = None
                    jiage = t.piaomianjiage
                    bili = utils.get_pool_percent(pool, t.chupiaohang)
                    edu = round(jiage * bili / 100, 2)
                    log.edu_chineipiao -= Decimal(jiage)
                    log.edu_keyong -= Decimal(edu)
                    log.feiyong_yewu += Decimal(jiage - edu)
                    pool.edu_keyong -= Decimal(edu)
                    pool.edu_chineipiao -= Decimal(jiage)
                    pool.save()
                t.t_status = 3
                t.sell_status = 4
                t.sellorder = order
                t.selltime = order.pub_date
                t.maipiaoren = request.POST['maipiaoren']
                t.maichujiage = round(float(request.POST['maichujiage' + str(t.piaomianjiage)]), 2)
                t.lirun = t.maichujiage - t.gourujiage
                t.save()
                order.money += t.maichujiage
                log.need_collect += Decimal(t.maichujiage)
                log.lirun_yewu += Decimal(t.lirun)
        order.total_sum = order.money
        order.needpay_sum = order.total_sum - order.payfee_sum
        order.save()
        utils.save_log(log, detail)
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
    card_data = Card.objects.all()
    feeform = MoneyForm(request.POST or None)
    context = {
        'order': order,
        'ticket_data': ticket_data,
        'card_data': card_data,
        'feeform': feeform,
    }
    if request.method == 'POST':
        if feeform.is_valid():
            money = feeform.cleaned_data.get('money')
            if 'zijinchipay' in request.POST.keys():
                # 使用预收付款
                if order.order_type == 1:
                    if money > order.needpay_sum:
                        context['errormsg'] = u'付款金额不能大于待支付金额'
                    elif money > order.customer.yufu_benjin:
                        context['errormsg'] = u'付款金额不能大于可用预付金额'
                    else:
                        log, detail = utils.create_log()
                        detail.add_detail_ticketorder(pk)
                        log.oper_type = 205
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.yushou -= Decimal(money)
                        log.need_pay -= Decimal(money)
                        utils.create_loan_pre_collect_fee(order.customer, 0 - money, log)
                        utils.create_ticket_order_fee(order, 0 - money, log)
                        utils.save_log(log, detail)
                        context['message'] = u'付款成功'
                elif order.order_type == 2:
                    if money > order.needpay_sum:
                        context['errormsg'] = u'收款金额不能大于待收取金额'
                    elif money > order.customer.yushou_benjin:
                        context['errormsg'] = u'收款金额不能大于可用预收金额'
                    else:
                        log, detail = utils.create_log()
                        detail.add_detail_ticketorder(pk)
                        log.oper_type = 206
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.yufu -= Decimal(money)
                        log.need_collect -= Decimal(money)
                        utils.create_loan_pre_pay_fee(order.customer, 0 - money, log)
                        utils.create_ticket_order_fee(order, money, log)
                        utils.save_log(log, detail)
                        context['message'] = u'收款成功'
            else:
                card = Card.objects.get(pk=int(request.POST['yinhangka']))
                if order.order_type == 1:
                    if money > order.needpay_sum:
                        context['errormsg'] = u'付款金额不能大于待支付金额'
                    else:
                        log, detail = utils.create_log()
                        detail.add_detail_ticketorder(pk)
                        detail.add_detail_card(card.pk)
                        log.oper_type = 203
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.need_pay -= Decimal(money)
                        utils.create_card_fee(card, 0 - money, log)
                        utils.create_ticket_order_fee(order, 0 - money, log)
                        utils.save_log(log, detail)
                        context['message'] = u'付款成功'
                elif order.order_type == 2:
                    if money > order.needpay_sum:
                        context['errormsg'] = u'收款金额不能大于待收取金额'
                    else:
                        log, detail = utils.create_log()
                        detail.add_detail_ticketorder(pk)
                        detail.add_detail_card(card.pk)
                        log.oper_type = 204
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.need_collect -= Decimal(money)
                        utils.create_card_fee(card, money, log)
                        utils.create_ticket_order_fee(order, money, log)
                        utils.save_log(log, detail)
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
            log, detail = utils.create_log()
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
            utils.save_log(log, detail)

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
