import datetime
from decimal import Decimal

from django.db import models


class BaseLoan(models.Model):
    benjin = models.FloatField(u'本金', default=0)
    lilv = models.FloatField(u'利率', default=0)
    lixi_begin_date = models.DateField(u'计息日期', auto_now_add=False)
    lixi_end_date = models.DateField(u'到期日期', auto_now_add=False)
    benjin_payed = models.FloatField(u'已还本金', default=0)
    benjin_needpay = models.FloatField(u'待还本金', default=0)
    lixi = models.FloatField(u'利息', default=0)
    lixi_payed = models.FloatField(u'已还利息', default=0)
    lixi_needpay = models.FloatField(u'待还利息', default=0)
    lixi_sum_date = models.DateField(u'结息日期', auto_now_add=False)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    is_payed = models.BooleanField(u'是否还清', default=False)
    is_end = models.BooleanField(u'是否到期', default=False)

    class Meta:
        abstract = True


class Card(models.Model):
    CARD_TYPE = (
        (1, u'私户'),
        (2, u'公户'),
    )
    card_type = models.IntegerField(
        u'账户类型',
        choices=CARD_TYPE,
        default=1,
    )
    name = models.CharField(u'银行卡', max_length=50)
    money = models.FloatField(u'金额', default=0)
    beizhu = models.CharField(u'备注', max_length=100)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    class Meta:
        verbose_name = '银行卡'
        verbose_name_plural = '银行卡'

    def __str__(self):
        return self.name


class Pool(models.Model):
    name = models.CharField(u'名称', max_length=50)
    yinhangka = models.ForeignKey(Card, related_name='pool_card', verbose_name=u'银行卡', blank=False, null=False)
    edu_keyong = models.DecimalField(u'可用额度', default=0, max_digits=10, decimal_places=2)
    edu_yiyong = models.DecimalField(u'已用额度', default=0, max_digits=10, decimal_places=2)
    edu_baozhengjin = models.DecimalField(u'保证金', default=0, max_digits=10, decimal_places=2)
    edu_chineipiao = models.DecimalField(u'池内票', default=0, max_digits=10, decimal_places=2)
    edu_licai = models.DecimalField(u'理财', default=0, max_digits=10, decimal_places=2)
    edu_chaoduandai = models.DecimalField(u'超短贷', default=0, max_digits=10, decimal_places=2)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期', auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(u'姓名', max_length=100)
    need_collect_benjin = models.FloatField(u'应收本金', default=0)
    need_collect_lixi = models.FloatField(u'应收利息', default=0)
    need_pay_benjin = models.FloatField(u'应付本金', default=0)
    need_pay_lixi = models.FloatField(u'应付利息', default=0)
    yufu_benjin = models.FloatField(u'预付本金', default=0)
    yufu_lixi = models.FloatField(u'预付利息', default=0)
    yushou_benjin = models.FloatField(u'预收本金', default=0)
    yushou_lixi = models.FloatField(u'预收利息', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_TYPE = (
        (1, u'待付款订单'),
        (2, u'待收款订单'),
    )
    order_type = models.IntegerField(
        u'订单类型',
        choices=ORDER_TYPE,
        default=1,
    )
    money = models.FloatField(u'合计应收付金额', default=0)
    ticket_sum = models.FloatField(u'合计票面价格', default=0)
    ticket_count = models.IntegerField(u'票据数目', default=0)
    fee_sum = models.FloatField(u'合计费用金额', default=0)
    fee_count = models.IntegerField(u'费用数目', default=0)
    payfee_sum = models.FloatField(u'已支付金额', default=0)
    payfee_count = models.IntegerField(u'已支付次数', default=0)
    total_sum = models.FloatField(u'总金额', default=0)
    needpay_sum = models.FloatField(u'剩余金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    customer = models.ForeignKey(Customer, related_name='ticket_order_customer', verbose_name=u'客户', blank=False,
                                 null=False)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return (u'%d' % (self.order_type))


class Loan_Order(BaseLoan):
    ORDER_TYPE = (
        (3, u'借款订单'),
        (4, u'贷款订单'),
    )
    order_type = models.IntegerField(
        u'订单类型',
        choices=ORDER_TYPE,
        default=3,
    )
    jiedairen = models.ForeignKey(Customer, related_name='loanorder_customer', verbose_name=u'借贷人', blank=False,
                                  null=False)
    yinhangka = models.ForeignKey(Card, related_name='loanorder_card', verbose_name=u'借贷卡', blank=False, null=False)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return (u'%d' % (self.order_type))


class Per_Detail(models.Model):
    ORDER_TYPE = (
        (5, u'预收票款'),
        (6, u'预付票款'),
        (7, u'预收款付账'),
        (8, u'预付款收票'),
    )
    order_type = models.IntegerField(
        u'费用类型',
        choices=ORDER_TYPE,
        default=5,
    )
    jiedairen = models.ForeignKey(Customer, related_name='pre_order_customer', verbose_name=u'客户', blank=False,
                                  null=False)
    money = models.FloatField(u'金额', default=0)
    yinhangka = models.ForeignKey(Card, related_name='pre_order_card', verbose_name=u'银行卡', blank=False, null=False)
    order = models.ForeignKey(Order, related_name='pre_order_pay', verbose_name=u'票据订单', blank=True, null=True)

    def __str__(self):
        return (u'%d' % (self.order_type))


class BaseTicket(models.Model):
    PAY_STATUS = (
        (1, u'待付款'),
        (2, u'已付款'),
    )
    SELL_STATUS = (
        (3, u'待收款'),
        (4, u'已收款'),
    )
    TICKET_STATUS = (
        (1, u'在库'),
        (2, u'待完成'),
        (5, u'在池'),
        (3, u'卖出'),
        (7, u'在池到期'),
    )
    TICKET_TYPES = (
        (1, u'纸票'),
        (2, u'电票'),
    )
    t_status = models.IntegerField(
        u'状态',
        choices=TICKET_STATUS,
        default=1,
    )
    t_type = models.IntegerField(
        u'类型',
        choices=TICKET_TYPES,
        default=1,
    )
    goumairiqi = models.DateTimeField(u'购买日期', auto_now_add=True)
    pool_in_riqi = models.DateField(u'入池日期', blank=True, null=True)
    qianpaipiaohao = models.CharField(u'前排票号', max_length=100, blank=True, null=True)
    piaohao = models.CharField(u'票号', max_length=100, blank=True, null=True)
    chupiaohang = models.CharField(u'出票行', max_length=100)
    chupiaoriqi = models.DateField(u'出票日期', )
    daoqiriqi = models.DateField(u'到期日期', )
    piaomianjiage = models.FloatField(u'票面价格(元)', default=0)
    gourujiage = models.FloatField(u'购入价格', default=0)
    paytime = models.DateTimeField(u'付款时间', blank=True, null=True)
    gongyingshang = models.CharField(u'供应商', max_length=100)
    pay_status = models.IntegerField(
        u'状态',
        choices=PAY_STATUS,
        default=1,
    )
    maichuriqi = models.DateTimeField(u'卖出日期', blank=True, null=True)
    maichujiage = models.FloatField(u'卖出价格', default=0)
    maipiaoren = models.CharField(u'买票人', max_length=100, blank=True, null=True)
    sell_status = models.IntegerField(
        u'状态',
        choices=SELL_STATUS,
        default=3,
    )
    selltime = models.DateTimeField(u'收款时间', blank=True, null=True)
    lirun = models.IntegerField(u'利润', default=0)

    class Meta:
        abstract = True


class Ticket(BaseTicket):
    pool_in = models.ForeignKey(Pool, related_name='t_pool_in', verbose_name=u'资金池', blank=True, null=True)
    gouruzijinchi = models.BooleanField(u'资金池购入', default=False)
    pool_buy = models.ForeignKey(Pool, related_name='t_pool_buy', verbose_name=u'资金池购入', blank=True, null=True)
    payedzijinchi = models.BooleanField(u'保证金还款', default=False)
    is_in_pay_car = models.BooleanField(u'付款购物车中', default=False)
    is_in_sell_car = models.BooleanField(u'收款购物车中', default=False)
    payorder = models.ForeignKey(Order, related_name='pay_order', verbose_name=u'付款订单', blank=True, null=True)
    sellorder = models.ForeignKey(Order, related_name='sell_order', verbose_name=u'收款订单', blank=True, null=True)

    class Meta:
        verbose_name = '票据'
        verbose_name_plural = '票据'

    def __str__(self):
        return self.gongyingshang


class SuperLoan(BaseLoan):
    pool = models.ForeignKey(Pool, related_name='super_loan_pool', verbose_name=u'资金池', blank=False, null=False)

    class Meta:
        verbose_name = '超短贷'
        verbose_name_plural = '超短贷'


class PoolLicai(models.Model):
    benjin = models.FloatField(u'本金', default=0)
    lilv = models.FloatField(u'利率', default=0)
    lixi = models.FloatField(u'利息', default=0)
    lixi_begin_date = models.DateField(u'计息日期', auto_now_add=False)
    lixi_end_date = models.DateField(u'到期日期', auto_now_add=False)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    is_front = models.BooleanField(u'利息前置', default=False)
    is_end = models.BooleanField(u'是否到期', default=False)
    is_payed = models.BooleanField(u'是否还清', default=False)
    yinhangka = models.ForeignKey(Card, related_name='licai_card', verbose_name=u'银行卡', blank=False, null=False)
    pool = models.ForeignKey(Pool, related_name='licai_pool', verbose_name=u'资金池', blank=False, null=False)
    beizhu = models.CharField(u'备注', max_length=255, default="", blank=True, null=True)

    class Meta:
        verbose_name = '理财'
        verbose_name_plural = '理财'


class PoolPercent(models.Model):
    pool = models.ForeignKey(Pool, related_name='percent_pool', verbose_name=u'资金池', blank=False, null=False)
    tags = models.CharField(u'标签', max_length=50)
    inpoolPer = models.FloatField(u'入池额度比例(%)', default=0)
    is_active = models.BooleanField(u'激活', default=True)

    class Meta:
        unique_together = ("pool", "tags")


class PoolPercentDetail(models.Model):
    inpoolPercent = models.ForeignKey(PoolPercent, related_name='pool_loan', verbose_name=u'超短贷', blank=True,
                                      null=True)
    inpoolPer = models.FloatField(u'入池额度比例', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)


class CardTrans(models.Model):
    fromCard = models.ForeignKey(Card, related_name='tran_from_card', verbose_name=u'转出账户', blank=False, null=False)
    money = models.FloatField(u'金额', default=0)
    toCard = models.ForeignKey(Card, related_name='tran_to_card', verbose_name=u'转入账户', blank=False, null=False)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)


class AllInfo(models.Model):
    xianjin = models.DecimalField(u'现金', default=0, max_digits=10, decimal_places=2)
    kucun = models.DecimalField(u'库存票', default=0, max_digits=10, decimal_places=2)
    edu_keyong = models.DecimalField(u'可用额度', default=0, max_digits=10, decimal_places=2)
    edu_yiyong = models.DecimalField(u'已用额度', default=0, max_digits=10, decimal_places=2)
    edu_baozhengjin = models.DecimalField(u'保证金', default=0, max_digits=10, decimal_places=2)
    edu_chineipiao = models.DecimalField(u'池内票', default=0, max_digits=10, decimal_places=2)
    edu_licai = models.DecimalField(u'理财', default=0, max_digits=10, decimal_places=2)
    edu_chaoduandai = models.DecimalField(u'超短贷', default=0, max_digits=10, decimal_places=2)
    need_collect = models.DecimalField(u'应收', default=0, max_digits=10, decimal_places=2)
    need_pay = models.DecimalField(u'应付', default=0, max_digits=10, decimal_places=2)
    yushou = models.DecimalField(u'预收', default=0, max_digits=10, decimal_places=2)
    yufu = models.DecimalField(u'预付', default=0, max_digits=10, decimal_places=2)
    feiyong_yewu = models.DecimalField(u'业务费用', default=0, max_digits=10, decimal_places=2)
    feiyong_ziben = models.DecimalField(u'资本费用', default=0, max_digits=10, decimal_places=2)
    feiyong_za = models.DecimalField(u'管理杂费', default=0, max_digits=10, decimal_places=2)
    lirun_yewu = models.DecimalField(u'业务利润', default=0, max_digits=10, decimal_places=2)
    lirun_ziben = models.DecimalField(u'资本收益', default=0, max_digits=10, decimal_places=2)
    lirun_za = models.DecimalField(u'其他利润', default=0, max_digits=10, decimal_places=2)

    class Meta:
        abstract = True


class DashBoard(AllInfo):
    day = models.DateField(u'统计日期', auto_created=False, primary_key=True)


class DashBoardSum(AllInfo):
    day = models.DateField(u'统计日期', auto_created=False, primary_key=True)


OPER_TYPE = (
    (101, u'新建开票'),
    (102, u'新建池开票'),
    (103, u'票据入库'),
    (104, u'票据入池'),
    (105, u'票据在池到期'),
    (106, u'票据导入'),
    (107, u'开票补充信息'),
    (108, u'池开票补充信息'),
    (201, u'新建待付款订单'),
    (202, u'新建待收款订单'),
    (203, u'现金付待付款订单'),
    (204, u'现金收待收款订单'),
    (205, u'使用预付款付待付款订单'),
    (206, u'使用预收款收待收款订单'),
    (301, u'新建应收款订单'),
    (302, u'新建应付款订单'),
    (303, u'应收款收本'),
    (304, u'应收款收息'),
    (305, u'应付款还本'),
    (306, u'应付款还息'),
    (307, u'新建预收款订单'),
    (308, u'新建预付款订单'),
    (309, u'应收付款结息'),
    (401, u'新建银行卡'),
    (402, u'银行卡存入'),
    (403, u'银行卡取出'),
    (404, u'银行卡转账'),
    (500, u'新建资金池'),
    (501, u'存入保证金'),
    (502, u'取出保证金'),
    (503, u'新增超短贷'),
    (504, u'超短贷还本'),
    (505, u'超短贷还息'),
    (506, u'池开票还款'),
    (507, u'超短贷结息'),
    (510, u'新增理财'),
    (511, u'理财前置收息'),
    (512, u'理财到期收款'),
)


class OperLog(AllInfo):
    oper_type = models.IntegerField(
        u'操作类型',
        choices=OPER_TYPE,
        default=101,
    )
    detail = models.CharField(u'相关票据卡', max_length=255, blank=False, null=False)
    contdetail = models.TextField(u'详情', blank=False, null=False)
    search_date = models.DateField(u'添加日期', auto_now_add=True)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = '操作记录'

    def __str__(self):
        return self.get_oper_type_display()


FeeDetail_Type = (
    (1, u'票据'),
    (2, u'票据订单'),
    (3, u'借贷订单'),
    (4, u'预收付款'),
    (41, u'预收款'),
    (42, u'预付款'),
    (5, u'银行卡'),
    (6, u'保证金'),
    (7, u'超短贷'),
    (8, u'理财'),
    (9, u'资金池'),
)


class FeeDetail(models.Model):
    oper_log = models.ForeignKey(OperLog, related_name='carddetail_log', verbose_name=u'操作详情', blank=False, null=False)
    money = models.FloatField(u'金额', default=0)
    beizhu = models.CharField(u'备注', max_length=255, default="", blank=True, null=True)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    fee_type = models.IntegerField(
        u'费用类型',
        choices=OPER_TYPE,
        default=1,
    )
    fee_detail_type = models.IntegerField(
        u'相关费用类型',
        choices=FeeDetail_Type,
        default=1,
    )
    fee_detail_pk = models.CharField(u'相关费用ID', max_length=100)


class MoneyWithCard(models.Model):
    money = models.FloatField(u'金额', default=0)
    card = models.ForeignKey(Card, related_name='money_card', verbose_name=u'银行卡', blank=False, null=False)


class MoneyWithCardPool(models.Model):
    money = models.FloatField(u'金额', default=0)
    card = models.ForeignKey(Card, related_name='moneys_card', verbose_name=u'银行卡', blank=False, null=False)
    pool = models.ForeignKey(Pool, related_name='moneys_pool', verbose_name=u'资金池', blank=False, null=False)


IMPORT_TYPE = (
    (1, u'库存'),
    (2, u'资金池'),
    (3, u'开票'),
    # (4, u'浙商福利'),
)


class Ticket_Import(models.Model):
    import_type = models.IntegerField(
        u'导入到',
        choices=IMPORT_TYPE,
        default=1,
    )
    pool = models.ForeignKey(Pool, related_name='import_pool', verbose_name=u'资金池', blank=True, null=True)
    detail = models.CharField(u'详情', max_length=255, blank=False, null=False)
    is_saved = models.BooleanField(u'保存', default=False)
    search_date = models.DateField(u'添加日期', auto_now_add=True)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)


class Ticket_Import_Detail(BaseTicket):
    inport_info = models.ForeignKey(Ticket_Import, related_name='t_import', verbose_name=u'导入', blank=False, null=False)
    zhiyalv = models.FloatField(u'质押率', default=100)
    saved = models.BooleanField(u'是否已保存', default=False)
    search_date = models.DateField(u'添加日期', auto_now_add=True)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)
    beizhu = models.CharField(u'备注', max_length=255, blank=True, null=True)
