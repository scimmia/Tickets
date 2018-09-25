import datetime

from django.db.models import Q, Sum
from django.shortcuts import render, redirect

from ticket import utils
from ticket.forms import SuperLoanForm, SuperLoanFeeForm, ProForm, PoolLicaiForm
from ticket.models import Ticket, SuperLoan, Card, Fee, SuperLoanFee, FeeDetail, PoolLicai
from ticket.utils import LogTemp


def pool_dash(request):
    pro_form = ProForm(request.POST or None)
    super_loan_form = SuperLoanForm(request.POST or None)
    licai_form = PoolLicaiForm(request.POST or None)

    context = {}
    if request.method == 'POST':
        if pro_form.is_valid():
            licai_form = PoolLicaiForm()
            super_loan_form = SuperLoanForm()
            pool = pro_form.save(commit=False)
            money = pool.money
            card = pool.card
            log = LogTemp()
            log.add_detail_pro()
            log.add_detail_card(card.pk)
            if pro_form.cleaned_data.get('p_status') == '2':
                money = 0 - money
                log.oper_type = 502
            else:
                log.oper_type = 501
            log.add_xianjin(0 - money)
            log.add_baozhengjin(money)
            log.save()
            utils.create_pro_fee(money, log)
            utils.create_card_fee(pool.card, 0 - money, log)
            context['message'] = u'保存保证金成功'
        elif super_loan_form.is_valid():
            pro_form = ProForm()
            licai_form = PoolLicaiForm()
            instance = super_loan_form.save(commit=False)
            if super_loan_form.cleaned_data.get('isMonthlilv') == '2':
                instance.lilv = super_loan_form.cleaned_data.get('lilv') * 1.2
            instance.benjin_needpay = super_loan_form.cleaned_data.get('benjin')
            instance.lixi_sum_date = instance.lixi_begin_date
            instance.save()
            log = LogTemp()
            log.oper_type = 503
            log.add_detail_superloan(instance.pk)
            log.add_chaoduandai(instance.benjin)
            log.save()
            utils.create_super_loan_fee(instance, instance.benjin, log)
            context['message'] = u'保存超短贷成功'
        elif licai_form.is_valid():
            pro_form = ProForm()
            super_loan_form = SuperLoanForm()
            instance = licai_form.save(commit=False)
            if licai_form.cleaned_data.get('isMonthlilv') == '2':
                instance.lilv = licai_form.cleaned_data.get('lilv') * 1.2
            days = (instance.lixi_end_date - instance.lixi_begin_date).days
            instance.lixi = round(instance.benjin * instance.lilv / 100 * days / 360, 2)
            today = datetime.date.today()
            if (instance.lixi_end_date - today).days <= 0:
                instance.is_end = True
            instance.save()
            instance.yinhangka.money -= instance.benjin
            instance.yinhangka.save()
            log = LogTemp()
            log.oper_type = 510
            log.add_detail_licai(instance.pk)
            log.add_detail_card(instance.yinhangka.pk)
            log.add_licai(instance.benjin)
            log.add_xianjin(0 - instance.benjin)
            log.save()
            utils.create_licai_fee(instance, instance.benjin, log)
            utils.create_card_fee(instance.yinhangka, 0 - instance.benjin, log)
            if instance.is_front:
                instance.yinhangka.money += instance.lixi
                instance.yinhangka.save()
                lixilog = LogTemp()
                lixilog.oper_type = 511
                lixilog.add_detail_licai(instance.pk)
                lixilog.add_detail_card(instance.yinhangka.pk)
                lixilog.add_xianjin(instance.lixi)
                lixilog.save()
                utils.create_licai_fee(instance, instance.lixi, lixilog)
                utils.create_card_fee(instance.yinhangka, instance.lixi, lixilog)
            context['message'] = u'保存理财成功'

    pro_form.fields['card'].required = True
    context['form'] = pro_form
    context['loanform'] = super_loan_form
    context['pool_licai_form'] = licai_form

    dash = utils.get_dash()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    count_t = Ticket.objects.filter(Q(t_status=5) & Q(daoqiriqi__gte=today)).count()
    count_chikai = Ticket.objects.filter(gouruzijinchi=True).count()
    sum_chikai = 0
    if count_chikai > 0:
        sum_chikai = Ticket.objects.filter(gouruzijinchi=True).aggregate(Sum('piaomianjiage')).get('piaomianjiage__sum')
    context['dash'] = dash
    context['today'] = today
    context['count_t'] = count_t
    context['sum_chikai'] = sum_chikai
    context['count_chikai'] = count_chikai

    fee_data = FeeDetail.objects.filter(fee_detail_type__in=[6, 7, 8]).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/pool_dash.html', context)


def pool_licai_lists(request):
    context = {}
    if request.method == 'POST':
        ids = request.POST['ids']
        if len(ids) > 0:
            licais = PoolLicai.objects.filter(id__in=ids.split(','))
            for t in licais:
                if t.is_end and (not t.is_payed):
                    t.is_payed = True
                    t.save()
                    log = LogTemp()
                    log.oper_type = 512
                    log.add_detail_licai(t.pk)
                    log.add_detail_card(t.yinhangka.pk)
                    log.add_licai(0 - t.benjin)
                    log.add_xianjin(t.benjin)
                    money = t.benjin
                    if not t.is_front:
                        money += t.lixi
                        log.add_xianjin(t.lixi)
                    log.save()
                    t.yinhangka.money += money
                    t.yinhangka.save()
                    utils.create_licai_fee(t, 0 - t.benjin, log)
                    utils.create_card_fee(t.yinhangka, money, log)
        context['message'] = u'收款成功'
    data = PoolLicai.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, data, 'ticket/pool_licais.html', context)


def super_loan_lists(request):
    super_loan_form = SuperLoanForm(request.POST or None)
    # 新建超短贷
    if request.method == 'POST':
        if super_loan_form.is_valid():
            instance = super_loan_form.save(commit=False)
            if super_loan_form.cleaned_data.get('isMonthlilv') == '2':
                instance.lilv = super_loan_form.cleaned_data.get('lilv') * 1.2
            instance.benjin_needpay = super_loan_form.cleaned_data.get('benjin')
            instance.lixi_sum_date = instance.lixi_begin_date
            instance.save()
            log = LogTemp()
            log.oper_type = 503
            log.add_detail_superloan(instance.pk)
            log.add_chaoduandai(instance.benjin)
            log.save()
            utils.create_super_loan_fee(instance, instance.benjin, log)
            return redirect('pool_dash')
    loan_data = SuperLoan.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, loan_data, 'ticket/pool_loans.html')


def super_loan(request, pk):
    order = SuperLoan.objects.get(pk=pk)
    card_data = Card.objects.all()
    poolfeeform = SuperLoanFeeForm(request.POST or None)
    context = {
        'poolfeeform': poolfeeform,
        'card_data': card_data,
        'order': order,
    }
    if request.method == 'POST':
        if poolfeeform.is_valid():
            money = poolfeeform.cleaned_data.get('money')
            if 'benjin' in request.POST.keys():
                if money > order.benjin_needpay:
                    context['message'] = u'金额不能大于待还本金'
                else:
                    log = LogTemp()
                    log.add_detail_superloan(pk)
                    log.oper_type = 504
                    utils.pay_super_loan_benjin(order, money)
                    log.add_chaoduandai(0 - money)
                    if 'zijinchipay' in request.POST.keys():
                        # 资金池还款
                        instance = SuperLoanFee()
                        instance.superloan = order
                        instance.money = 0 - money
                        instance.name = '保证金还超短贷本金'
                        instance.save()
                        log.add_baozhengjin(0 - money)
                        log.save()
                        utils.create_pro_fee(0 - money, log)
                        pass
                    else:
                        # 银行卡还款
                        card = Card.objects.get(pk=int(request.POST['yinhangka']))
                        log.add_detail_card(card.pk)
                        log.add_xianjin(0 - money)
                        log.save()
                        utils.create_card_fee(card, 0 - money, log)
                    utils.create_super_loan_fee(order, 0 - money, log)
                    context['message'] = u'还款成功'
                pass
            elif 'lixi' in request.POST.keys():
                if money > order.lixi_needpay:
                    context['message'] = u'金额不能大于待还利息'
                else:
                    log = LogTemp()
                    log.add_detail_superloan(pk)
                    log.oper_type = 505
                    log.add_feiyong_yewu(money)
                    utils.pay_super_loan_lixi(order, money)
                    if 'zijinchipay' in request.POST.keys():
                        # 资金池还款
                        instance = SuperLoanFee()
                        instance.superloan = order
                        instance.money = 0 - money
                        instance.name = '保证金还超短贷利息'
                        instance.save()
                        log.add_baozhengjin(0 - money)
                        log.save()
                        utils.create_pro_fee(0 - money, log)
                        pass
                    else:
                        # 银行卡还款
                        card = Card.objects.get(pk=int(request.POST['yinhangka']))
                        log.add_detail_card(card.pk)
                        log.add_xianjin(0 - money)
                        log.save()
                        utils.create_card_fee(card, 0 - money, log)
                    utils.create_super_loan_fee(order, 0 - money, log)
                    context['message'] = u'还息成功'
                pass
    fee_data = FeeDetail.objects.filter(fee_detail_type=7, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/pool_superloan.html', context)


def pool_tickets(request):
    context = {
        'gongyingshang': utils.get_list_from_tickets('gongyingshang'),
        'maipiaoren': utils.get_list_from_tickets('maipiaoren'),
    }
    if request.method == 'POST':
        if 'ids' in request.POST.keys():
            ids = request.POST['ids']
            log = LogTemp()
            log.oper_type = 506
            if len(ids) > 0:
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if not t.payedzijinchi:
                        t.payedzijinchi = True
                        t.save()
                        log.add_detail_ticket(t.pk)
                        log.add_baozhengjin(0 - t.gourujiage)
            log.save()
            context['message'] = u'还款成功'
            pass
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_data = Ticket.objects.filter(Q(gouruzijinchi=True) & Q(payedzijinchi=False) & Q(daoqiriqi__lte=today)).order_by(
        '-goumairiqi')
    return utils.get_paged_page(request, raw_data, 'ticket/pool_tickets.html', context)
