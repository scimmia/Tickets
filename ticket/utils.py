import datetime
import json
from decimal import Decimal

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render

from ticket import view_tools
from ticket.models import OperLog, DashBoard, Card, FeeDetail, InpoolPercent, Ticket


def create_fee_detail(money, fee_detail_type, fee_detail_pk, log_temp):
    if money != 0:
        fee_detail = FeeDetail()
        fee_detail.oper_log = log_temp.log
        fee_detail.money = money
        fee_detail.fee_type = log_temp.log.oper_type
        fee_detail.fee_detail_type = fee_detail_type
        fee_detail.fee_detail_pk = fee_detail_pk
        fee_detail.save()
    pass


def create_ticket_order_fee(order, money, log_temp):
    create_fee_detail(money, 2, order.pk, log_temp)
    pass


def create_card_fee(card, money, log_temp):
    card.money = card.money + money
    card.save()
    create_fee_detail(money, 5, card.pk, log_temp)
    pass


def create_loan_fee(loan, money, log_temp):
    create_fee_detail(money, 3, loan.pk, log_temp)
    pass


def create_loan_pre_fee(order, money, log_temp):
    create_fee_detail(money, 4, order.pk, log_temp)
    pass


def create_loan_pre_collect_fee(customer, money, log_temp):
    customer.yushou_benjin += money
    customer.save()
    create_fee_detail(money, 41, customer.pk, log_temp)
    pass


def create_loan_pre_pay_fee(customer, money, log_temp):
    customer.yufu_benjin += money
    customer.save()
    create_fee_detail(money, 42, customer.pk, log_temp)
    pass


def create_pro_fee(money, log_temp):
    create_fee_detail(money, 6, u'保证金', log_temp)


def create_super_loan_fee(super_loan, money, log_temp):
    create_fee_detail(money, 7, super_loan.pk, log_temp)


def create_licai_fee(licai, money, log_temp):
    create_fee_detail(money, 8, licai.pk, log_temp)


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
        log = LogTemp()
        log.oper_type = 507
        log.add_detail_superloan(order.pk)
        log.add_need_pay(lixi)
        log.save()
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
        log = LogTemp()
        log.oper_type = 309
        log.add_detail_loanorder(order.pk)
        log.add_need_pay(lixi)
        log.save()
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


def get_pool_percent(tag=u'!默认!'):
    if InpoolPercent.objects.filter(tags__contains=tag).count() == 0:
        if InpoolPercent.objects.filter(tags='!默认!').count() == 0:
            view_tools.create_pool_percent('!默认!', 100)
            return 100
        return InpoolPercent.objects.get(tags='!默认!').inpoolPer
    return InpoolPercent.objects.filter(tags__contains=tag).last().inpoolPer


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
    data_list, page_range, count, page_nums = pagination(request, data, 50)
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


class LogTemp:
    def __init__(self):
        self.log = OperLog()
        self.xianjin = 0
        self.kucun = 0
        self.edu_keyong = 0
        self.edu_yiyong = 0
        self.edu_baozhengjin = 0
        self.edu_chineipiao = 0
        self.edu_licai = 0
        self.edu_chaoduandai = 0
        self.need_collect = 0
        self.need_pay = 0
        self.yushou = 0
        self.yufu = 0
        self.feiyong_yewu = 0
        self.feiyong_ziben = 0
        self.feiyong_za = 0
        self.lirun_yewu = 0
        self.lirun_ziben = 0
        self.lirun_za = 0
        self.oper_type = 0
        self.detail = []
        self.contdetail = []
        pass

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

    def add_xianjin(self, money):
        self.xianjin += money

    def add_kucun(self, money):
        self.kucun += money

    def add_keyong(self, money):
        self.edu_keyong += money

    def add_yiyong(self, money):
        self.edu_yiyong += money

    def add_baozhengjin(self, money):
        self.edu_baozhengjin += money
        self.add_keyong(money)

    def add_chineipiao(self, money):
        self.edu_chineipiao += money

    def add_licai(self, money):
        self.edu_licai += money
        self.add_keyong(money)

    def add_chaoduandai(self, money):
        self.edu_chaoduandai += money
        self.add_keyong(0 - money)
        self.add_yiyong(money)

    def add_need_collect(self, money):
        self.need_collect += money

    def add_need_pay(self, money):
        self.need_pay += money

    def add_yushou(self, money):
        self.yushou += money

    def add_yufu(self, money):
        self.yufu += money

    def add_feiyong_yewu(self, money):
        self.feiyong_yewu += money

    def add_feiyong_ziben(self, money):
        self.feiyong_ziben += money

    def add_feiyong_za(self, money):
        self.feiyong_za += money

    def add_lirun_yewu(self, money):
        self.lirun_yewu += money

    def add_lirun_ziben(self, money):
        self.lirun_ziben += money

    def add_lirun_za(self, money):
        self.lirun_za += money

    def build_detail(self):
        if len(self.detail) > 0:
            if self.xianjin != 0:
                self.contdetail.append({'cont': u'银行卡', 'money': self.xianjin})
            if self.kucun != 0:
                self.contdetail.append({'cont': u'库存', 'money': self.kucun})
            if self.edu_keyong != 0:
                self.contdetail.append({'cont': u'可用额度', 'money': self.edu_keyong})
            if self.edu_yiyong != 0:
                self.contdetail.append({'cont': u'已用额度', 'money': self.edu_yiyong})
            if self.edu_baozhengjin != 0:
                self.contdetail.append({'cont': u'保证金', 'money': self.edu_baozhengjin})
            if self.edu_chineipiao != 0:
                self.contdetail.append({'cont': u'池内票', 'money': self.edu_chineipiao})
            if self.edu_licai != 0:
                self.contdetail.append({'cont': u'理财', 'money': self.edu_licai})
            if self.edu_chaoduandai != 0:
                self.contdetail.append({'cont': u'超短贷', 'money': self.edu_chaoduandai})
            if self.need_collect != 0:
                self.contdetail.append({'cont': u'待收', 'money': self.need_collect})
            if self.need_pay != 0:
                self.contdetail.append({'cont': u'待付', 'money': self.need_pay})
            if self.yushou != 0:
                self.contdetail.append({'cont': u'预收', 'money': self.yushou})
            if self.yufu != 0:
                self.contdetail.append({'cont': u'预付', 'money': self.yufu})
            if self.feiyong_yewu != 0:
                self.contdetail.append({'cont': u'业务费用', 'money': self.feiyong_yewu})
            if self.feiyong_ziben != 0:
                self.contdetail.append({'cont': u'资本费用', 'money': self.feiyong_ziben})
            if self.feiyong_za != 0:
                self.contdetail.append({'cont': u'管理杂费', 'money': self.feiyong_za})
            if self.lirun_yewu != 0:
                self.contdetail.append({'cont': u'业务利润', 'money': self.lirun_yewu})
            if self.lirun_ziben != 0:
                self.contdetail.append({'cont': u'资本收益', 'money': self.lirun_ziben})
            if self.lirun_za != 0:
                self.contdetail.append({'cont': u'其他利润', 'money': self.lirun_za})

    def save(self):
        self.log.xianjin = Decimal(self.xianjin)
        self.log.kucun = Decimal(self.kucun)
        self.log.edu_keyong = Decimal(self.edu_keyong)
        self.log.edu_yiyong = Decimal(self.edu_yiyong)
        self.log.edu_baozhengjin = Decimal(self.edu_baozhengjin)
        self.log.edu_chineipiao = Decimal(self.edu_chineipiao)
        self.log.edu_licai = Decimal(self.edu_licai)
        self.log.edu_chaoduandai = Decimal(self.edu_chaoduandai)
        self.log.need_collect = Decimal(self.need_collect)
        self.log.need_pay = Decimal(self.need_pay)
        self.log.yushou = Decimal(self.yushou)
        self.log.yufu = Decimal(self.yufu)
        self.log.feiyong_yewu = Decimal(self.feiyong_yewu)
        self.log.feiyong_ziben = Decimal(self.feiyong_ziben)
        self.log.feiyong_za = Decimal(self.feiyong_za)
        self.log.lirun_yewu = Decimal(self.lirun_yewu)
        self.log.lirun_ziben = Decimal(self.lirun_ziben)
        self.log.lirun_za = Decimal(self.lirun_za)
        self.log.oper_type = self.oper_type
        self.log.detail = json.dumps(self.detail)
        self.build_detail()
        self.log.contdetail = json.dumps(self.contdetail)
        self.log.save()
        self.save_dash()

    def save_dash(self):
        dash = get_dash()
        dash.xianjin += self.log.xianjin
        dash.kucun += self.log.kucun
        dash.edu_keyong += self.log.edu_keyong
        dash.edu_yiyong += self.log.edu_yiyong
        dash.edu_baozhengjin += self.log.edu_baozhengjin
        dash.edu_chineipiao += self.log.edu_chineipiao
        dash.edu_licai += self.log.edu_licai
        dash.edu_chaoduandai += self.log.edu_chaoduandai
        dash.need_collect += self.log.need_collect
        dash.need_pay += self.log.need_pay
        dash.yushou += self.log.yushou
        dash.yufu += self.log.yufu
        dash.feiyong_yewu += self.log.feiyong_yewu
        dash.feiyong_ziben += self.log.feiyong_ziben
        dash.feiyong_za += self.log.feiyong_za
        dash.lirun_yewu += self.log.lirun_yewu
        dash.lirun_ziben += self.log.lirun_ziben
        dash.lirun_za += self.log.lirun_za
        dash.save()
