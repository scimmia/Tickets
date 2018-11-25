import os
from decimal import Decimal

import xlrd
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ticket import utils, view_loan
from ticket.forms import TicketForm, TicketEditForm, MoneyForm, TicketTransForm, CardForm, TicketImportForm
from ticket.models import Card, Ticket, Order, FeeDetail, OperLog, Pool, \
    Ticket_Import, Ticket_Import_Detail


# 增加
@login_required
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
            log, detail = utils.create_log(request.user.last_name)
            log.oper_type = 101
            while counter <= times:
                counter += 1
                instance.pk = None
                if instance.gouruzijinchi and instance.t_status != 2:
                    instance.gongyingshang = instance.pool_buy.name
                    instance.pay_status = 2
                    instance.gourujiage = instance.piaomianjiage
                instance.save()
                detail.add_detail_ticket(instance.pk)
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
@login_required
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
                log, detail = utils.create_log(request.user.last_name)
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
                    instance.gongyingshang = instance.pool_buy.name
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


@login_required
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
                log, detail = utils.create_log(request.user.last_name)
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


@login_required
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
        if len(ids) > 0:
            if index == 1:
                Ticket.objects.filter(id__in=ids.split(',')).update(is_in_pay_car=True)
                context['message'] = u'加入成功'
            elif index == 2:
                Ticket.objects.filter(id__in=ids.split(',')).update(is_in_sell_car=True)
                context['message'] = u'加入成功'
        else:
            context['errormsg'] = u'请选择至少一张票据'
    if index == 1:
        raw_data = Ticket.objects.filter(~Q(t_status=2), pay_status=1, payorder=None, gourujiage__gt=0,
                                         is_in_pay_car=False).order_by(
            '-goumairiqi')
    else:
        raw_data = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None, is_in_sell_car=False).order_by(
            '-goumairiqi')
    list_template = 'ticket/ticket_toselect.html'
    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def ticket_needpay(request):
    return ticket_needselect(request, 1)


@login_required
def ticket_needcollect(request):
    return ticket_needselect(request, 2)


def ticket_needselect_car(request, index):
    context = {
        'index': index,
        'maipiaoren': get_ticketlists('maipiaoren'),
    }
    if request.method == 'POST':
        ids = request.POST['ids']
        if len(ids) > 0:
            if 'remove_ticket' in request.POST.keys():
                if index == 1:
                    Ticket.objects.filter(id__in=ids.split(','), ).update(is_in_pay_car=False)
                    context['message'] = u'删除成功'
                elif index == 2:
                    Ticket.objects.filter(id__in=ids.split(',')).update(is_in_sell_car=False)
                    context['message'] = u'删除成功'
                pass
            elif 'create_order' in request.POST.keys():
                order = Order()
                order.order_type = int(request.POST['ordertype'])
                order.customer = view_loan.get_customer_by_name(request.POST['maipiaoren'])
                order.save()
                log, detail = utils.create_log(request.user.last_name)
                detail.add_detail_ticketorder(order.pk)
                # 待付款订单
                if order.order_type == 1:
                    log.oper_type = 201
                    tickets = Ticket.objects.filter(~Q(t_status=2), pay_status=1, payorder=None, gourujiage__gt=0,
                                                    is_in_pay_car=True, id__in=ids.split(',')).order_by('-goumairiqi')
                    for t in tickets:
                        detail.add_detail_ticket(t.pk)
                        order.ticket_count += 1
                        order.ticket_sum += t.piaomianjiage
                        order.money += t.gourujiage
                        log.need_pay += Decimal(t.gourujiage)
                        t.pay_status = 2
                        t.payorder = order
                        t.paytime = order.pub_date
                        t.is_in_pay_car = False
                        t.save()
                # 待收款订单
                elif order.order_type == 2:
                    log.oper_type = 202
                    tickets = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None, is_in_sell_car=True,
                                                    id__in=ids.split(',')).order_by('-goumairiqi')
                    for t in tickets:
                        detail.add_detail_ticket(t.pk)
                        order.ticket_count += 1
                        order.ticket_sum += t.piaomianjiage
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
                        t.is_in_sell_car = False
                        t.sell_status = 4
                        t.sellorder = order
                        t.selltime = order.pub_date
                        t.maipiaoren = request.POST['maipiaoren']
                        t.maichujiage = round(float(request.POST[',' + str(t.pk) + ',']), 2)
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
        else:
            context['errormsg'] = u'请选择至少一张票据'
    if index == 1:
        raw_data = Ticket.objects.filter(~Q(t_status=2), pay_status=1, payorder=None, gourujiage__gt=0,
                                         is_in_pay_car=True).order_by(
            '-goumairiqi')
    else:
        raw_data = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None, is_in_sell_car=True).order_by(
            '-piaomianjiage')
        prices = Ticket.objects.filter(~Q(t_status=2), sell_status=3, sellorder=None, is_in_sell_car=True) \
            .values('piaomianjiage', 'chupiaohang', 'daoqiriqi') \
            .annotate(max=Count('pk'), ids=utils.Concat('pk')).order_by('piaomianjiage')
        context['prices'] = prices
    context['data'] = raw_data
    return render(request, 'ticket/ticket_order_preview.html', context)


@login_required
def ticket_needpay_car(request):
    return ticket_needselect_car(request, 1)


@login_required
def ticket_needcollect_car(request):
    return ticket_needselect_car(request, 2)


def ticket_orderlist(request, index):
    list_template = 'ticket/ticket_orders.html'
    raw_data = Order.objects.filter(order_type=index).order_by('-pub_date')
    context = {
        'index': index,
    }
    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def ticket_payorders(request):
    return ticket_orderlist(request, 1)


@login_required
def ticket_sellorders(request):
    return ticket_orderlist(request, 2)


@login_required
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
            if 'yushoufupay' in request.POST.keys():
                if order.order_type == 1:
                    # 待付款订单，使用预付款
                    if money > order.needpay_sum:
                        context['errormsg'] = u'付款金额不能大于待支付金额'
                    elif money > order.customer.yufu_benjin:
                        context['errormsg'] = u'付款金额不能大于可用预付金额'
                    else:
                        log, detail = utils.create_log(request.user.last_name)
                        detail.add_detail_ticketorder(pk)
                        log.oper_type = 205
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.yufu -= Decimal(money)
                        log.need_pay -= Decimal(money)
                        utils.create_loan_yu_fu_fee(order.customer, 0 - money, log)
                        utils.create_ticket_order_fee(order, 0 - money, log)
                        utils.save_log(log, detail)
                        context['message'] = u'付款成功'
                elif order.order_type == 2:
                    # 待收款订单，使用预收款
                    if money > order.needpay_sum:
                        context['errormsg'] = u'收款金额不能大于待收取金额'
                    elif money > order.customer.yushou_benjin:
                        context['errormsg'] = u'收款金额不能大于可用预收金额'
                    else:
                        log, detail = utils.create_log(request.user.last_name)
                        detail.add_detail_ticketorder(pk)
                        log.oper_type = 206
                        order.payfee_count += 1
                        order.payfee_sum += money
                        order.needpay_sum -= money
                        order.save()
                        log.yushou -= Decimal(money)
                        log.need_collect -= Decimal(money)
                        utils.create_loan_yu_shou_fee(order.customer, 0 - money, log)
                        utils.create_ticket_order_fee(order, money, log)
                        utils.save_log(log, detail)
                        context['message'] = u'收款成功'
            else:
                card = Card.objects.get(pk=int(request.POST['yinhangka']))
                if order.order_type == 1:
                    # 待付款订单，使用现金
                    if money > order.needpay_sum:
                        context['errormsg'] = u'付款金额不能大于待支付金额'
                    else:
                        log, detail = utils.create_log(request.user.last_name)
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
                    # 待收款订单，使用现金
                    if money > order.needpay_sum:
                        context['errormsg'] = u'收款金额不能大于待收取金额'
                    else:
                        log, detail = utils.create_log(request.user.last_name)
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


@login_required
def ticket_imports(request):
    form = TicketImportForm(request.POST or None)
    list_template = 'ticket/ticket_imports.html'
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            book = xlrd.open_workbook(path + 'tmp.csv')
            print("The number of worksheets is {0}".format(book.nsheets))
            print("Worksheet name(s): {0}".format(book.sheet_names()))
            sh = book.sheet_by_index(0)
            print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
            if instance.import_type != 2:
                instance.pool = None
            instance.detail = ''
            instance.save()
            ticketsImports = []
            # 入库
            if instance.import_type == 1:
                for rx in range(sh.nrows):
                    row = (sh.row_values(rx))
                    if sh.cell_type(rowx=rx, colx=0) == 3:
                        m = Ticket_Import_Detail()
                        m.inport_info = instance
                        m.qianpaipiaohao = row[1]
                        m.piaohao = str(row[2])
                        m.gongyingshang = row[9]
                        m.chupiaohang = row[3]
                        if sh.cell(rx, 0).ctype == 3:
                            m.goumairiqi = xlrd.xldate_as_datetime((row[0]), book.datemode)
                        else:
                            print(rx)
                            continue
                        if sh.cell(rx, 4).ctype == 3:
                            m.chupiaoriqi = xlrd.xldate_as_datetime((row[4]), book.datemode)
                        else:
                            print(rx)
                            continue
                        if sh.cell(rx, 5).ctype == 3:
                            m.daoqiriqi = xlrd.xldate_as_datetime((row[5]), book.datemode)
                        else:
                            print(rx)
                            continue
                        m.piaomianjiage = (row[6])
                        if sh.cell(rx, 8).ctype == 3:
                            m.gourujiage = row[8]
                        m.beizhu = row[10]
                        ticketsImports.append(m)
            # 入池
            elif instance.import_type == 2:
                for rx in range(sh.nrows):
                    row = (sh.row_values(rx))
                    if len(row) == 14:
                        if row[5].startswith('2'):
                            m = Ticket_Import_Detail()
                            m.inport_info = instance
                            m.piaohao = row[2]
                            m.gongyingshang = row[0]
                            m.chupiaohang = row[4]
                            m.chupiaoriqi = row[5].replace(' ', '').replace('\t', '')
                            m.daoqiriqi = row[6].replace(' ', '').replace('\t', '')
                            m.piaomianjiage = (row[3])
                            m.pool_in_riqi = row[11].replace(' ', '').replace('\t', '')
                            m.goumairiqi = row[13].replace(' ', '').replace('\t', '')
                            if row[7] == '电票':
                                m.t_type = 2
                            if sh.cell(rx, 12).ctype == 2:
                                m.zhiyalv = float(row[12])
                            m.gourujiage = m.piaomianjiage
                            ticketsImports.append(m)
            # 开票
            elif instance.import_type == 3:
                for rx in range(sh.nrows):
                    row = (sh.row_values(rx))
                    if row[5].startswith('2'):
                        m = Ticket_Import_Detail()
                        m.inport_info = instance
                        m.piaohao = row[0]
                        m.gongyingshang = row[1]
                        m.maipiaoren = row[2]
                        m.chupiaohang = row[11]
                        m.chupiaoriqi = row[5].replace(' ', '').replace('\t', '')
                        m.daoqiriqi = row[6].replace(' ', '').replace('\t', '')
                        m.piaomianjiage = (row[3])
                        m.gourujiage = m.piaomianjiage
                        m.t_type = 2
                        ticketsImports.append(m)
            # 浙商福利
            # elif instance.import_type == 4:
            #     tickets_temp = []
            #     for rx in range(sh.nrows):
            #         row = (sh.row_values(rx))
            #         try:
            #             if row[9] and len(row[9]) > 0:
            #                 m = Ticket()
            #                 n = sh.cell(rx, 0).ctype
            #                 n = sh.cell_type(rx, 0)
            #                 if sh.cell(rx, 0).ctype == 3:
            #                     m.goumairiqi = xlrd.xldate_as_datetime((row[0]), book.datemode)
            #                 else:
            #                     print(rx)
            #                     continue
            #                 m.qianpaipiaohao = row[1]
            #                 m.piaohao = row[2]
            #                 m.gongyingshang = row[9]
            #                 m.chupiaohang = row[3]
            #                 if sh.cell(rx, 4).ctype == 3:
            #                     m.chupiaoriqi = xlrd.xldate_as_datetime((row[4]), book.datemode)
            #                 else:
            #                     print(rx)
            #                     continue
            #                 if sh.cell(rx, 5).ctype == 3:
            #                     m.daoqiriqi = xlrd.xldate_as_datetime((row[5]), book.datemode)
            #                 else:
            #                     print(rx)
            #                     continue
            #                 # m.chupiaoriqi = row[4].replace(' ', '').replace('\t', '')
            #                 # m.daoqiriqi = row[5].replace(' ', '').replace('\t', '')
            #                 m.piaomianjiage = float(row[6])
            #                 m.gourujiage = float(row[8])
            #                 if sh.cell(rx, 10).ctype == 3:
            #                     m.maichuriqi = xlrd.xldate_as_datetime((row[10]), book.datemode)
            #                 # m.maichuriqi = row[10].replace(' ', '').replace('\t', '')
            #                 m.maichujiage = float(row[12])
            #                 m.maipiaoren = row[13]
            #                 m.lirun = float(row[14])
            #                 m.t_type = 3
            #                 m.pay_status = 2
            #                 m.sell_status = 4
            #                 tickets_temp.append(m)
            #         except:
            #             print(rx)
            #             pass
            #     if len(tickets_temp) > 0:
            #         Ticket.objects.bulk_create(tickets_temp)
            if len(ticketsImports) > 0:
                Ticket_Import_Detail.objects.bulk_create(ticketsImports)

            return redirect('ticket_import_detail', instance.id)
            pass

    raw_data = Ticket_Import.objects.all().order_by('-pub_date')
    context = {
        'form': form,
    }
    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def ticket_import_detail(request, pk):
    info = Ticket_Import.objects.get(pk=pk)
    data = Ticket_Import_Detail.objects.filter(inport_info=pk)
    if request.method == "POST":
        if info.is_saved:
            message = u'已保存'
        else:
            message = u'保存成功'
            data.update(saved=True)
            tickets = []
            for item in data:
                m = Ticket()
                m.t_type = item.t_type
                m.qianpaipiaohao = item.qianpaipiaohao
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.gourujiage
                m.paytime = item.paytime
                m.gongyingshang = item.gongyingshang
                m.pay_status = item.pay_status
                m.maichuriqi = item.maichuriqi
                m.maichujiage = item.maichujiage
                m.maipiaoren = item.maipiaoren
                m.sell_status = item.sell_status
                m.selltime = item.selltime
                m.selltime = item.selltime
                # 入库
                if info.import_type == 1:
                    m.t_status = 1
                    pass
                # 入池
                elif info.import_type == 2:
                    m.t_status = 5
                    m.pool_in = info.pool
                    pass
                # 开票
                elif info.import_type == 3:
                    pass
                tickets.append(m)
                pass
            if len(tickets) > 0:
                Ticket.objects.bulk_create(tickets)
            info.is_saved = True
            info.save()

    list_template = 'ticket/ticket_import_detail.html'
    return render(request, 'ticket/ticket_import_detail.html', locals())
