import datetime
import json
from decimal import Decimal

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render

from ticket.models import OperLog, DashBoard, FeeDetail, Ticket, PoolPercent, PoolPercentDetail


def create_fee_detail(money, fee_detail_type, fee_detail_pk, log_temp):
    if money != 0:
        fee_detail = FeeDetail()
        fee_detail.money = money
        fee_detail.fee_detail_type = fee_detail_type
        fee_detail.fee_detail_pk = fee_detail_pk
        if isinstance(log_temp, OperLog):
            fee_detail.oper_log = log_temp
            fee_detail.fee_type = log_temp.oper_type
        fee_detail.save()
    pass


def create_ticket_order_fee(order, money, log_temp):
    create_fee_detail(money, 2, order.pk, log_temp)
    pass


def create_card_fee(card, money, log_temp):
    card.money += money
    card.save()
    if isinstance(log_temp, OperLog):
        log_temp.xianjin += Decimal(money)
    create_fee_detail(money, 5, card.pk, log_temp)
    pass


def create_loan_fee(loan, money, log_temp):
    create_fee_detail(money, 3, loan.pk, log_temp)
    pass


def create_loan_pre_fee(order, money, log_temp):
    create_fee_detail(money, 4, order.pk, log_temp)
    pass


def create_loan_yu_shou_fee(customer, money, log_temp):
    customer.yushou_benjin += money
    customer.save()
    create_fee_detail(money, 41, customer.pk, log_temp)
    pass


def create_loan_yu_fu_fee(customer, money, log_temp):
    customer.yufu_benjin += money
    customer.save()
    create_fee_detail(money, 42, customer.pk, log_temp)
    pass


def create_pro_fee(pool, money, log_temp):
    pool.edu_baozhengjin += Decimal(money)
    pool.edu_keyong += Decimal(money)
    pool.save()
    log_temp.edu_baozhengjin += Decimal(money)
    log_temp.edu_keyong += Decimal(money)
    log_temp.save()
    create_fee_detail(money, 9, pool.pk, log_temp)


def create_super_loan_fee(super_loan, money, log_temp):
    super_loan.pool.edu_chaoduandai += Decimal(money)
    super_loan.pool.edu_keyong -= Decimal(money)
    super_loan.pool.edu_yiyong += Decimal(money)
    super_loan.pool.save()
    log_temp.edu_chaoduandai += Decimal(money)
    log_temp.edu_keyong -= Decimal(money)
    log_temp.edu_yiyong += Decimal(money)
    log_temp.save()
    create_fee_detail(money, 9, super_loan.pool.pk, log_temp)
    create_fee_detail(money, 7, super_loan.pk, log_temp)


def create_licai_fee(licai, money, log_temp):
    licai.pool.edu_licai += Decimal(money)
    licai.pool.edu_keyong += Decimal(money)
    licai.pool.save()
    if isinstance(log_temp, OperLog):
        log_temp.edu_licai += Decimal(money)
        log_temp.edu_keyong += Decimal(money)
        # log_temp.save()
    create_fee_detail(money, 9, licai.pool.pk, log_temp)


# 结息（借贷及超短贷）
def count_loan_lixi(order):
    addLixi = 0
    if not order.is_end:
        today = datetime.date.today()
        if (today - order.lixi_end_date).days >= 0:
            order.is_end = True
            order.save()
            today = order.lixi_end_date
        days = (today - order.lixi_sum_date).days
        if days > 0:
            addLixi = round(order.benjin_needpay * order.lilv / 100 * days / 360, 2)
            order.lixi = round(addLixi + order.lixi, 2)
            order.lixi_needpay = round(addLixi + order.lixi_needpay, 2)
            order.lixi_sum_date = today
            order.save()
        elif days == 0:
            order.is_end = True
            order.save()
    return addLixi


# 支付本金（借贷及超短贷）
def payLoanBenjin(order, money):
    order.benjin_payed = order.benjin_payed + money
    order.benjin_needpay = order.benjin_needpay - money
    order.is_payed = order.benjin_needpay == 0 and order.lixi_needpay == 0
    order.save()


# 支付利息（借贷及超短贷）
def payLoanLixi(order, money):
    order.lixi_payed = order.lixi_payed + money
    order.lixi_needpay = order.lixi_needpay - money
    order.is_payed = order.benjin_needpay == 0 and order.lixi_needpay == 0
    order.save()


# 结息（超短贷）
def count_super_loan_lixi(order):
    lixi = count_loan_lixi(order)
    if lixi > 0:
        log, detail = create_log()
        log.oper_type = 507
        detail.add_detail_superloan(order.pk)
        log.need_pay += Decimal(lixi)
        save_log(log, detail)
    return lixi


# 支付本金（超短贷）
def pay_super_loan_benjin(order, money):
    count_super_loan_lixi(order)
    payLoanBenjin(order, money)


# 支付利息（超短贷）
def pay_super_loan_lixi(order, money):
    count_super_loan_lixi(order)
    payLoanLixi(order, money)


# 结息（借贷款）
def count_order_loan_lixi(order):
    lixi = count_loan_lixi(order)
    if lixi > 0:
        log, detail = create_log()
        log.oper_type = 309
        detail.add_detail_loanorder(order.pk)
        log.need_pay += Decimal(lixi)
        save_log(log, detail)
    return lixi


# 支付本金（借贷款）
def pay_order_loan_benjin(order, money):
    addLixi = count_order_loan_lixi(order)
    payLoanBenjin(order, money)
    customer = order.jiedairen
    if order.order_type == 3:
        customer.need_collect_benjin -= money
        customer.need_collect_lixi += addLixi
        customer.save()
    elif order.order_type == 4:
        customer.need_pay_benjin -= money
        customer.need_pay_lixi += addLixi
        customer.save()


# 支付利息（借贷款）
def pay_order_loan_lixi(order, money):
    addLixi = count_order_loan_lixi(order)
    payLoanLixi(order, money)
    customer = order.jiedairen
    if order.order_type == 3:
        customer.need_collect_lixi += (addLixi - money)
        customer.save()
    elif order.order_type == 4:
        customer.need_pay_lixi += (addLixi - money)
        customer.save()


def create_pool_percent(pool, tag, inpoolPer):
    try:
        obj, created = PoolPercent.objects.update_or_create(
            pool=pool, tags=tag,
            defaults={'inpoolPer': inpoolPer},
        )
        temp = PoolPercentDetail()
        temp.inpoolPercent = obj
        temp.inpoolPer = inpoolPer
        temp.save()
        return True
    except:
        return False


def get_pool_percent(pool, tag=u'!默认!'):
    if PoolPercent.objects.filter(pool=pool, tags__contains=tag).count() == 0:
        if PoolPercent.objects.filter(pool=pool, tags='!默认!').count() == 0:
            create_pool_percent(pool, '!默认!', 100)
            return 100
        return PoolPercent.objects.get(pool=pool, tags='!默认!').inpoolPer
    return PoolPercent.objects.filter(tags__contains=tag).last().inpoolPer


def get_dash(day=datetime.date.today()):
    dash, created = DashBoard.objects.get_or_create(
        day=day,
    )
    return dash


def get_list_from_tickets(col):
    gys = Ticket.objects.values(col).annotate(Count('id'))
    t = []
    for g in gys:
        list.insert(t, 0, g[col])
    return t


def get_query(request):
    kwargs = {}
    query = ''
    for key in request.GET.keys():
        value = request.GET[(key)]
        # 刨去其中的token和page选项
        if key != 'csrfmiddlewaretoken' and key != 'page' and (len(value) > 0):
            kwargs[key] = value
            query += '&' + key + '=' + value
    return kwargs, query


def get_paged_page(request, raw_data, list_template, context={}):
    kwargs, query = get_query(request)
    data = raw_data.filter(**kwargs)
    data_list, page_range, count, page_nums = pagination(request, data, 100)
    context['data'] = data_list
    context['query'] = query
    context['page_range'] = page_range
    context['count'] = count
    context['page_nums'] = page_nums
    return render(request, list_template, context)


# 分页函数
def pagination(request, queryset, display_amount=10, after_range_num=5, before_range_num=4):
    # 按参数分页

    try:
        # 从提交来的页面获得page的值
        page = int(request.GET.get("page", 1))
        # 如果page值小于1，那么默认为第一页
        if page < 1:
            page = 1
    # 若报异常，则page为第一页
    except ValueError:
        page = 1
    # 引用Paginator类
    paginator = Paginator(queryset, display_amount)
    # 总计的数据条目
    count = paginator.count
    # 合计页数
    num_pages = paginator.num_pages

    try:
        # 尝试获得分页列表
        objects = paginator.page(page)
    # 如果页数不存在
    except EmptyPage:
        # 获得最后一页
        objects = paginator.page(paginator.num_pages)
    # 如果不是一个整数
    except PageNotAnInteger:
        # 获得第一页
        objects = paginator.page(1)
    # 根据参数配置导航显示范围
    temp_range = paginator.page_range

    # 如果页面很小
    if (page - before_range_num) <= 0:
        # 如果总页面比after_range_num大，那么显示到after_range_num
        if temp_range[-1] > after_range_num:
            page_range = range(1, after_range_num + 1)
        # 否则显示当前页
        else:
            page_range = range(1, temp_range[-1] + 1)
    # 如果页面比较大
    elif (page + after_range_num) > temp_range[-1]:
        # 显示到最大页
        page_range = range(page - before_range_num, temp_range[-1] + 1)
    # 否则在before_range_num和after_range_num之间显示
    else:
        page_range = range(page - before_range_num + 1, page + after_range_num)
    # 返回分页相关参数
    return objects, page_range, count, num_pages


class LogDetailTemp:
    def __init__(self):
        self.detail = []
        pass

    def get_save_detail(self):
        return json.dumps(self.detail)

    def add_detail(self, pktype, pk):
        self.detail.append({'pktype': pktype, 'pk': pk})
        pass

    def add_detail_ticket(self, pk):
        self.add_detail(1, pk)

    def add_detail_ticketorder(self, pk):
        self.add_detail(2, pk)

    def add_detail_loanorder(self, pk):
        self.add_detail(3, pk)

    def add_detail_predetail(self, pk):
        self.add_detail(4, pk)

    def add_detail_card(self, pk):
        self.add_detail(5, pk)

    def add_detail_pro(self):
        self.add_detail(6, u'保证金')

    def add_detail_superloan(self, pk):
        self.add_detail(7, pk)

    def add_detail_licai(self, pk):
        self.add_detail(8, pk)

    def add_detail_pool(self, pk):
        self.add_detail(9, pk)


def create_log():
    detail = LogDetailTemp()
    log = OperLog()
    log.save()
    return log, detail


def save_log(log, detail):
    log.detail = detail.get_save_detail()
    log.save()
    save_log_to_dash(log)


def save_log_to_dash(log):
    try:
        dash = get_dash()
        dash.xianjin += Decimal(log.xianjin)
        dash.kucun += Decimal(log.kucun)
        dash.edu_keyong += Decimal(log.edu_keyong)
        dash.edu_yiyong += Decimal(log.edu_yiyong)
        dash.edu_baozhengjin += Decimal(log.edu_baozhengjin)
        dash.edu_chineipiao += Decimal(log.edu_chineipiao)
        dash.edu_licai += Decimal(log.edu_licai)
        dash.edu_chaoduandai += Decimal(log.edu_chaoduandai)
        dash.need_collect += Decimal(log.need_collect)
        dash.need_pay += Decimal(log.need_pay)
        dash.yushou += Decimal(log.yushou)
        dash.yufu += Decimal(log.yufu)
        dash.feiyong_yewu += Decimal(log.feiyong_yewu)
        dash.feiyong_ziben += Decimal(log.feiyong_ziben)
        dash.feiyong_za += Decimal(log.feiyong_za)
        dash.lirun_yewu += Decimal(log.lirun_yewu)
        dash.lirun_ziben += Decimal(log.lirun_ziben)
        dash.lirun_za += Decimal(log.lirun_za)
        dash.save()
    except:
        pass
    pass
