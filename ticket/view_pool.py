import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render

from ticket import utils
from ticket.forms import SuperLoanForm, ProForm, PoolLicaiForm, PoolForm, PoolPercentForm, MoneyBeizhuForm
from ticket.models import Ticket, SuperLoan, Card, FeeDetail, PoolLicai, Pool, OperLog, PoolPercent, \
    PoolPercentDetail
from ticket.utils import create_pool_percent


@login_required
def pool_dash(request):
    pool_form = PoolForm(request.POST or None)
    pro_form = ProForm(request.POST or None)
    super_loan_form = SuperLoanForm(request.POST or None)
    licai_form = PoolLicaiForm(request.POST or None)

    context = {}
    if request.method == 'POST':
        log, detail = utils.create_log(request.user.last_name)
        # 新建资金池
        if pool_form.is_valid():
            pro_form = ProForm()
            licai_form = PoolLicaiForm()
            super_loan_form = SuperLoanForm()
            pool = pool_form.save()
            detail.add_detail_pool(pool.pk)
            detail.add_detail_card(pool.yinhangka.pk)
            log.oper_type = 500
            utils.save_log(log, detail)
            context['message'] = u'新建资金池成功'
        # 存取保证金
        elif pro_form.is_valid():
            pool_form = PoolForm()
            licai_form = PoolLicaiForm()
            super_loan_form = SuperLoanForm()
            pro = pro_form.save(commit=False)
            money = pro.money
            pool = pro.pool
            card = pool.yinhangka
            detail.add_detail_pool(pool.pk)
            detail.add_detail_card(card.pk)
            if pro_form.cleaned_data.get('p_status') == '2':
                money = 0 - money
                log.oper_type = 502
            else:
                log.oper_type = 501
            utils.create_pro_fee(pool, money, log)
            utils.create_card_fee(card, 0 - money, log)
            utils.save_log(log, detail)
            context['message'] = u'保存保证金成功'
        #     新建超短贷
        elif super_loan_form.is_valid():
            pool_form = PoolForm()
            pro_form = ProForm()
            licai_form = PoolLicaiForm()
            instance = super_loan_form.save(commit=False)
            if super_loan_form.cleaned_data.get('super_isMonthlilv') == '2':
                instance.lilv = super_loan_form.cleaned_data.get('lilv') * 12 / 10
            instance.benjin_needpay = super_loan_form.cleaned_data.get('benjin')
            instance.lixi_sum_date = instance.lixi_begin_date
            instance.save()
            log.oper_type = 503
            detail.add_detail_pool(instance.pool.pk)
            detail.add_detail_card(instance.pool.yinhangka.pk)
            detail.add_detail_superloan(instance.pk)
            utils.create_card_fee(instance.pool.yinhangka,instance.benjin,log)
            utils.create_super_loan_fee(instance, instance.benjin, log)
            utils.save_log(log, detail)
            context['message'] = u'保存超短贷成功'
        #     新建理财
        elif licai_form.is_valid():
            pool_form = PoolForm()
            pro_form = ProForm()
            super_loan_form = SuperLoanForm()
            instance = licai_form.save(commit=False)
            instance.yinhangka = instance.pool.yinhangka
            if licai_form.cleaned_data.get('isMonthlilv') == '2':
                instance.lilv = licai_form.cleaned_data.get('lilv') * 12 / 10
            days = (instance.lixi_end_date - instance.lixi_begin_date).days
            instance.lixi = instance.benjin * instance.lilv / 100 * days / 360
            today = datetime.date.today()
            if (instance.lixi_end_date - today).days <= 0:
                instance.is_end = True
            instance.save()
            log.oper_type = 510
            detail.add_detail_pool(instance.pool.pk)
            detail.add_detail_licai(instance.pk)
            detail.add_detail_card(instance.yinhangka.pk)
            utils.create_licai_fee(instance, instance.benjin, log)
            utils.create_card_fee(instance.yinhangka, 0 - instance.benjin, log)
            utils.save_log(log, detail)
            if instance.is_front:
                lixilog, lixidetail = utils.create_log(request.user.last_name)
                lixilog.oper_type = 511
                lixidetail.add_detail_licai(instance.pk)
                lixidetail.add_detail_card(instance.yinhangka.pk)
                utils.create_card_fee(instance.yinhangka, instance.lixi, lixilog)
                utils.save_log(lixilog, lixidetail)
            context['message'] = u'保存理财成功'

    context['pool_form'] = pool_form
    context['form'] = pro_form
    context['loanform'] = super_loan_form
    context['pool_licai_form'] = licai_form

    # dash = utils.get_dash()
    dash = Pool.objects.aggregate(Sum('edu_keyong'), Sum('edu_yiyong'), Sum('edu_baozhengjin'), Sum('edu_chineipiao'),
                                  Sum('edu_licai'), Sum('edu_chaoduandai'))
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

    pool_data = Pool.objects.filter().order_by('-update_date')
    return utils.get_paged_page(request, pool_data, 'ticket/pool_dash.html', context)


@login_required
def pool_licai_lists(request):
    context = {}
    if request.method == 'POST':
        ids = request.POST['ids']
        if len(ids) > 0:
            licais = PoolLicai.objects.filter(id__in=ids.split(','))
            licai_count = 0
            for t in licais:
                if t.is_end and (not t.is_payed):
                    t.is_payed = True
                    t.save()
                    log, detail = utils.create_log(request.user.last_name)
                    log.oper_type = 512
                    detail.add_detail_pool(t.pool.pk)
                    detail.add_detail_licai(t.pk)
                    detail.add_detail_card(t.yinhangka.pk)
                    money = t.benjin
                    if not t.is_front:
                        money += t.lixi
                        log.lirun_yewu += Decimal(t.lixi)
                    utils.create_licai_fee(t, 0 - t.benjin, log)
                    utils.create_card_fee(t.yinhangka, money, log)
                    utils.save_log(log, detail)
                    licai_count += 1
            if licai_count > 0:
                context['message'] = (u'对%d条到期理财收款成功' % licai_count)
            else:
                context['errormsg'] = u'请选择至少一条“到期”理财'
        else:
            context['errormsg'] = u'请选择至少一条理财'
    data = PoolLicai.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, data, 'ticket/pool_licais.html', context)


@login_required
def super_loan_lists(request):
    loan_data = SuperLoan.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, loan_data, 'ticket/pool_loans.html')


@login_required
def super_loan(request, pk):
    order = SuperLoan.objects.get(pk=pk)
    card_data = Card.objects.all()
    poolfeeform = MoneyBeizhuForm(request.POST or None)
    context = {
        'poolfeeform': poolfeeform,
        'card_data': card_data,
        'order': order,
    }
    if request.method == 'POST':
        if poolfeeform.is_valid():
            money = (poolfeeform.cleaned_data.get('money'))
            beizhu = poolfeeform.cleaned_data.get('beizhu')
            if 'benjin' in request.POST.keys():
                if money > order.benjin_needpay:
                    context['errormsg'] = u'金额不能大于待还本金'
                else:
                    log, detail = utils.create_log(request.user.last_name)
                    detail.add_detail_superloan(pk)
                    log.oper_type = 504
                    if 'zijinchipay' in request.POST.keys():
                        # 资金池还款
                        detail.add_detail_pool(order.pool.pk)
                        utils.create_pro_fee(order.pool, 0 - money, log)
                        pass
                    else:
                        # 银行卡还款
                        card = Card.objects.get(pk=int(request.POST['yinhangka']))
                        detail.add_detail_card(card.pk)
                        utils.create_card_fee(card, 0 - money, log, beizhu)
                    utils.pay_super_loan_benjin(order, money)
                    utils.create_super_loan_fee(order, 0 - money, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'还款成功'
                pass
            elif 'lixi' in request.POST.keys():
                if money > order.lixi_needpay:
                    context['errormsg'] = u'金额不能大于待还利息'
                else:
                    log, detail = utils.create_log(request.user.last_name)
                    detail.add_detail_superloan(pk)
                    log.oper_type = 505
                    log.feiyong_yewu += Decimal(money)
                    utils.pay_super_loan_lixi(order, money)
                    if 'zijinchipay' in request.POST.keys():
                        # 资金池还款
                        detail.add_detail_pool(order.pool.pk)
                        utils.create_pro_fee(order.pool, 0 - money, log)
                        pass
                    else:
                        # 银行卡还款
                        card = Card.objects.get(pk=int(request.POST['yinhangka']))
                        detail.add_detail_card(card.pk)
                        utils.create_card_fee(card, 0 - money, log, beizhu)
                    utils.create_fee_detail(0 - money, 7, order.pk, log, beizhu)
                    utils.save_log(log, detail)
                    context['message'] = u'还息成功'
                pass
    fee_data = FeeDetail.objects.filter(fee_detail_type=7, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/pool_superloan.html', context)


@login_required
def pool_tickets(request):
    context = {
        'gongyingshang': utils.get_list_from_tickets('gongyingshang'),
        'maipiaoren': utils.get_list_from_tickets('maipiaoren'),
    }
    if request.method == 'POST':
        if 'ids' in request.POST.keys():
            ids = request.POST['ids']
            log, detail = utils.create_log(request.user.last_name)
            log.oper_type = 506
            if len(ids) > 0:
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if not t.payedzijinchi:
                        t.payedzijinchi = True
                        t.save()
                        detail.add_detail_ticket(t.pk)
                        log.edu_baozhengjin -= Decimal(t.gourujiage)
            utils.save_log(log, detail)
            context['message'] = u'还款成功'
            pass
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_data = Ticket.objects.filter(Q(gouruzijinchi=True) & Q(payedzijinchi=False) & Q(daoqiriqi__lte=today)).order_by(
        '-goumairiqi')
    return utils.get_paged_page(request, raw_data, 'ticket/pool_tickets.html', context)


@login_required
def pool_detail(request, pk):
    pool = get_object_or_404(Pool, pk=pk)
    context = {
        'dash': pool,
    }

    fee_data = FeeDetail.objects.filter(fee_detail_type=9, fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/pool_detail.html', context)


@login_required
def pool_percent_list(request):
    form = PoolPercentForm(request.POST or None)
    pools = Pool.objects.all()
    if PoolPercent.objects.filter(tags='!默认!').count() < len(pools):
        for pool in pools:
            create_pool_percent(pool, '!默认!', 100)
    if request.method == 'POST':
        if form.is_valid():
            t = form.save(commit=False)
            inpoolPer = request.POST['inpoolPer']
            if create_pool_percent(t.pool, t.tags, inpoolPer):
                message = u'保存成功'
            else:
                message = u'保存失败'

    data = PoolPercent.objects.all().order_by('tags')

    return render(request, 'ticket/inpoolPer_list.html', locals())


@login_required
def pool_percent_detail(request, pk):
    pool_percent = PoolPercent.objects.get(pk=pk)
    if request.method == 'POST':
        inpoolPer = request.POST['inpoolPer']
        try:
            pool_percent.inpoolPer = inpoolPer
            pool_percent.save()
            temp = PoolPercentDetail()
            temp.inpoolPercent = pool_percent
            temp.inpoolPer = inpoolPer
            temp.save()
            message = u'保存成功'
        except:
            message = u'保存失败'
    data = PoolPercentDetail.objects.filter(inpoolPercent=pool_percent).order_by('-pub_date')
    item = data[0]
    return render(request, 'ticket/inpoolPer.html', locals())
