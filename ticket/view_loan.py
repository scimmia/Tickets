from decimal import Decimal

from django.contrib.auth.decorators import login_required

from ticket import utils
from ticket.forms import LoanForm, LoanPreForm, MoneyWithCardForm
from ticket.models import Customer, Loan_Order, FeeDetail


def get_customer_by_name(name):
    try:
        customer = Customer.objects.get(name=name)
    except:
        customer = Customer(name=name)
        customer.save()
    return customer


# 应收款
def create_need_collect(customer, instance, isMonthlilv, username):
    money = instance.benjin
    instance.jiedairen = customer
    instance.order_type = 3
    if isMonthlilv:
        instance.lilv = instance.lilv * 12 / 10
    instance.benjin_needpay = money
    instance.lixi_sum_date = instance.lixi_begin_date
    instance.save()
    customer.need_collect_benjin += money
    customer.is_collect_acctive = True
    customer.save()
    log, detail = utils.create_log(username)
    log.oper_type = 301
    detail.add_detail_loanorder(instance.pk)
    detail.add_detail_card(instance.yinhangka.pk)
    log.need_collect += Decimal(money)
    utils.create_loan_fee(instance, money, log)
    utils.create_card_fee(instance.yinhangka, 0 - money, log)
    utils.save_log(log, detail)


@login_required
def need_collect_customers(request):
    loanform = LoanForm(request.POST or None)
    customerlist = Customer.objects.all().order_by('name')
    context = {
        'index': 3,
        'loanform': loanform,
        'customerlist': customerlist,
    }
    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = get_customer_by_name(request.POST['jiedairen'])
            create_need_collect(customer, instance, loanform.cleaned_data.get('isMonthlilv') == '2',
                                request.user.last_name)
            context['message'] = u'保存成功'
    raw_data = Customer.objects.filter(is_collect_acctive=True).order_by('-pub_date')
    list_template = 'ticket/loan_xx_customers.html'

    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def need_collect_lists(request, pk):
    list_template = 'ticket/loan_orders.html'
    loanform = LoanForm(request.POST or None)
    context = {
        'index': 3,
        'loanform': loanform,
    }

    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = Customer.objects.get(pk=pk)
            create_need_collect(customer, instance, loanform.cleaned_data.get('isMonthlilv') == '2', request.user.last_name)
            context['message'] = u'保存成功'
    raw_data = Loan_Order.objects.filter(order_type=3, jiedairen=pk).order_by('-pub_date')

    return utils.get_paged_page(request, raw_data, list_template, context)


def need_collect_order(request, order):
    pk = order.pk
    feeform = MoneyWithCardForm(request.POST or None)
    context = {
        'feeform': feeform,
        'order': order,
    }
    if request.method == 'POST':
        if feeform.is_valid():
            instance = feeform.save(commit=False)
            money = instance.money
            card = instance.card
            beizhu = feeform.cleaned_data.get('beizhu')
            log, detail = utils.create_log(request.user.last_name)
            detail.add_detail_loanorder(pk)
            detail.add_detail_card(card.pk)
            if 'benjin' in request.POST.keys():
                if feeform.cleaned_data.get('money') > order.benjin_needpay:
                    context['errormsg'] = u'金额不能大于应收本金'
                else:
                    utils.pay_order_loan_benjin(order, money)
                    log.oper_type = 303
                    log.need_collect -= Decimal(money)
                    utils.create_card_fee(card, money, log, beizhu)
                    utils.create_loan_fee(order, money, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'保存成功'
                pass
            elif 'lixi' in request.POST.keys():
                if feeform.cleaned_data.get('money') > order.lixi_needpay:
                    context['errormsg'] = u'金额不能大于待收利息'
                else:
                    utils.pay_order_loan_lixi(order, money)
                    log.oper_type = 304
                    log.lirun_yewu += Decimal(money)
                    utils.create_card_fee(card, money, log, beizhu)
                    utils.create_loan_fee(order, money, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'保存成功'
                pass

    fee_data = FeeDetail.objects.filter(fee_detail_type=3, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/loan_order.html', context)


# 应付款
def create_need_pay(customer, instance, isMonthlilv, username):
    money = instance.benjin
    instance.jiedairen = customer
    instance.order_type = 4
    if isMonthlilv:
        instance.lilv = instance.lilv * 12 / 10
    instance.benjin_needpay = money
    instance.lixi_sum_date = instance.lixi_begin_date
    instance.save()
    customer.need_pay_benjin += money
    customer.is_pay_acctive = True
    customer.save()
    log, detail = utils.create_log(username)
    log.oper_type = 302
    detail.add_detail_loanorder(instance.pk)
    detail.add_detail_card(instance.yinhangka.pk)
    log.need_collect -= Decimal(money)
    utils.create_loan_fee(instance, 0 - money, log)
    utils.create_card_fee(instance.yinhangka, money, log)
    utils.save_log(log, detail)


@login_required
def need_pay_customers(request):
    loanform = LoanForm(request.POST or None)
    customerlist = Customer.objects.all().order_by('name')

    context = {
        'index': 4,
        'loanform': loanform,
        'customerlist': customerlist,
    }
    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = get_customer_by_name(request.POST['jiedairen'])
            create_need_pay(customer, instance, loanform.cleaned_data.get('isMonthlilv') == '2', request.user.last_name)
            context['message'] = u'保存成功'
    raw_data = Customer.objects.filter(is_pay_acctive=True).order_by('-pub_date')
    list_template = 'ticket/loan_xx_customers.html'

    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def need_pay_lists(request, pk):
    list_template = 'ticket/loan_orders.html'
    loanform = LoanForm(request.POST or None)
    context = {
        'index': 4,
        'loanform': loanform,
    }

    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = Customer.objects.get(pk=pk)
            create_need_pay(customer, instance, loanform.cleaned_data.get('isMonthlilv') == '2', request.user.last_name)
            context['message'] = u'保存成功'
    raw_data = Loan_Order.objects.filter(order_type=4, jiedairen=pk).order_by('-pub_date')

    return utils.get_paged_page(request, raw_data, list_template, context)


def need_pay_order(request, order):
    pk = order.pk
    feeform = MoneyWithCardForm(request.POST or None)
    context = {
        'feeform': feeform,
        'order': order,
    }
    if request.method == 'POST':
        if feeform.is_valid():
            instance = feeform.save(commit=False)
            money = instance.money
            card = instance.card
            beizhu = feeform.cleaned_data.get('beizhu')
            log, detail = utils.create_log(request.user.last_name)
            detail.add_detail_loanorder(pk)
            detail.add_detail_card(card.pk)
            if 'benjin' in request.POST.keys():
                if feeform.cleaned_data.get('money') > order.benjin_needpay:
                    context['errormsg'] = u'金额不能大于应付本金'
                else:
                    utils.pay_order_loan_benjin(order, money)
                    log.oper_type = 305
                    log.need_pay -= Decimal(money)
                    utils.create_card_fee(card, 0 - money, log, beizhu)
                    utils.create_loan_fee(order, money, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'保存成功'
                pass
            elif 'lixi' in request.POST.keys():
                if feeform.cleaned_data.get('money') > order.lixi_needpay:
                    context['errormsg'] = u'金额不能大于待付利息'
                else:
                    utils.pay_order_loan_lixi(order, money)
                    log.oper_type = 306
                    log.feiyong_yewu += Decimal(money)
                    utils.create_card_fee(card, 0 - money, log, beizhu)
                    utils.create_loan_fee(order, money, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'保存成功'
                pass

    fee_data = FeeDetail.objects.filter(fee_detail_type=3, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/loan_order.html', context)


@login_required
def loanorder(request, pk):
    order = Loan_Order.objects.get(pk=pk)
    if order.order_type == 3:
        return need_collect_order(request, order)
    elif order.order_type == 4:
        return need_pay_order(request, order)


@login_required
def pre_collect_customers(request):
    loanform = LoanPreForm(request.POST or None)
    list_template = 'ticket/loan_xx_customers.html'
    customerlist = Customer.objects.values('name')

    context = {
        'index': 5,
        'loanform': loanform,
        'customerlist': customerlist,
    }
    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = get_customer_by_name(request.POST['jiedairen'])
            customer.is_yushou_acctive = True
            customer.save()
            money = instance.money
            card = instance.yinhangka
            instance.jiedairen = customer
            instance.order_type = 5
            instance.save()
            log, detail = utils.create_log(request.user.last_name)
            log.oper_type = 307
            detail.add_detail_predetail(instance.pk)
            detail.add_detail_card(card.pk)
            log.yushou += Decimal(money)
            utils.create_card_fee(card, money, log)
            utils.create_loan_yu_shou_fee(customer, money, log)
            utils.save_log(log, detail)
            context['message'] = u'保存成功'
    raw_data = Customer.objects.filter(is_yushou_acctive = True).order_by('-pub_date')

    return utils.get_paged_page(request, raw_data, list_template, context)


# 预付款
@login_required
def pre_pay_customers(request):
    loanform = LoanPreForm(request.POST or None)
    list_template = 'ticket/loan_xx_customers.html'
    customerlist = Customer.objects.all().order_by('name')

    context = {
        'index': 6,
        'loanform': loanform,
        'customerlist': customerlist,
    }
    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            customer = get_customer_by_name(request.POST['jiedairen'])
            customer.is_yufu_acctive = True
            customer.save()
            money = instance.money
            card = instance.yinhangka
            instance.jiedairen = customer
            instance.order_type = 6
            instance.save()
            log, detail = utils.create_log(request.user.last_name)
            log.oper_type = 308
            detail.add_detail_predetail(instance.pk)
            detail.add_detail_card(card.pk)
            log.yufu += Decimal(money)
            utils.create_card_fee(card, 0 - money, log)
            utils.create_loan_yu_fu_fee(customer, money, log)
            utils.save_log(log, detail)
            context['message'] = u'保存成功'
    raw_data = Customer.objects.filter(is_yufu_acctive = True).order_by('-pub_date')
    return utils.get_paged_page(request, raw_data, list_template, context)


@login_required
def pre_collect_list(request, pk):
    context = {
        'index': 1,
    }
    fee_data = FeeDetail.objects.filter(fee_detail_type=41, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/loan_pre_order.html', context)


@login_required
def pre_pay_list(request, pk):
    context = {
        'index': 2,
    }
    fee_data = FeeDetail.objects.filter(fee_detail_type=42, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/loan_pre_order.html', context)
