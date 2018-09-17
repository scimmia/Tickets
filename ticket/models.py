from django.db import models

# Create your models here.
class BaseLoan(models.Model):
    benjin = models.FloatField(u'本金', default=0)
    lilv = models.FloatField(u'利率', default=0)
    lixi_begin_date = models.DateField(u'计息日期', auto_now_add=False)
    benjin_payed = models.FloatField(u'已还本金', default=0)
    benjin_needpay = models.FloatField(u'待还本金', default=0)
    lixi = models.FloatField(u'利息', default=0)
    lixi_payed = models.FloatField(u'已还利息', default=0)
    lixi_needpay = models.FloatField(u'待还利息', default=0)
    lixi_sum_date = models.DateField(u'结息日期', auto_now_add=False)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    is_payed = models.BooleanField(u'是否还清', default=False)

    class Meta:
        abstract = True

class Card(models.Model):
    CARD_TYPE= (
        (1,u'私户'),
        (2,u'公户'),
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

class Order(models.Model):
    ORDER_TYPE= (
        (1,u'付款订单'),
        (2,u'收款订单'),
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
    payfee_count = models.IntegerField(u'已支付数目', default=0)
    total_sum = models.FloatField(u'总金额', default=0)
    needpay_sum = models.FloatField(u'剩余金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return (u'%d' % (self.order_type))

class Customer(models.Model):
    name = models.CharField(u'姓名', max_length=100)
    borrow_benjin = models.FloatField(u'借款本金', default=0)
    borrow_lixi = models.FloatField(u'借款利息', default=0)
    loan_benjin = models.FloatField(u'贷款本金', default=0)
    loan_lixi = models.FloatField(u'贷款利息', default=0)
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


class Loan_Order(BaseLoan):
    ORDER_TYPE= (
        (3,u'借款订单'),
        (4,u'贷款订单'),
    )
    order_type = models.IntegerField(
        u'订单类型',
        choices=ORDER_TYPE,
        default=3,
    )
    jiedairen = models.ForeignKey( Customer, related_name='loanorder_customer', verbose_name=u'借贷人' , blank=False,null=False)
    yinhangka = models.ForeignKey( Card, related_name='loanorder_card', verbose_name=u'借贷卡' , blank=False,null=False)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return (u'%d' % (self.order_type))


class Per_Detail(models.Model):
    ORDER_TYPE= (
        (5,u'预收票款'),
        (6,u'预付票款'),
        (7,u'预收款付账'),
        (8,u'预付款收票'),
    )
    order_type = models.IntegerField(
        u'费用类型',
        choices=ORDER_TYPE,
        default=5,
    )
    jiedairen = models.ForeignKey( Customer, related_name='pre_order_customer', verbose_name=u'客户' , blank=False,null=False)
    money = models.FloatField(u'金额', default=0)
    yinhangka = models.ForeignKey( Card, related_name='pre_order_card', verbose_name=u'银行卡' , blank=False,null=False)
    order = models.ForeignKey( Order, related_name='pre_order_pay', verbose_name=u'票据订单' ,  blank=True,null=True)

    def __str__(self):
        return (u'%d' % (self.order_type))

class Ticket(models.Model):
    PAY_STATUS= (
        (1,u'待付款'),
        (2,u'已付款'),
    )
    SELL_STATUS= (
        (3,u'待收款'),
        (4,u'已收款'),
    )
    TICKET_STATUS= (
        (1,u'在库'),
        (5,u'在池'),
        (3,u'卖出'),
        (7,u'在池到期'),
    )
    TICKET_TYPES= (
        (1,u'纸票'),
        (2,u'电票'),
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
    qianpaipiaohao = models.CharField(u'前排票号', max_length=100, blank=True,null=True)
    piaohao = models.CharField(u'票号', max_length=100, blank=True,null=True)
    chupiaohang = models.CharField(u'出票行', max_length=100)
    chupiaoriqi = models.DateField(u'出票日期', )
    daoqiriqi = models.DateField(u'到期日期', )
    piaomianjiage = models.FloatField(u'票面价格(元)', default=0)
    gourujiage = models.FloatField(u'购入价格', default=0)
    gouruzijinchi = models.BooleanField(u'资金池购入', default=False)
    payedzijinchi = models.BooleanField(u'保证金还款', default=False)
    gongyingshang = models.CharField(u'供应商', max_length=100)
    pay_status = models.IntegerField(
        u'状态',
        choices=PAY_STATUS,
        default=1,
    )
    payorder = models.ForeignKey( Order, related_name='pay_order', verbose_name=u'付款订单' ,  blank=True,null=True)
    paytime = models.DateTimeField(u'付款时间', blank=True,null=True)
    maichuriqi = models.DateTimeField(u'卖出日期', blank=True,null=True)
    maichujiage = models.FloatField(u'卖出价格', default=0)
    maipiaoren = models.CharField(u'买票人', max_length=100, blank=True,null=True)
    sell_status = models.IntegerField(
        u'状态',
        choices=SELL_STATUS,
        default=3,
    )
    sellorder = models.ForeignKey( Order, related_name='sell_order', verbose_name=u'收款订单' ,  blank=True,null=True)
    selltime = models.DateTimeField(u'收款时间', blank=True,null=True)
    lirun = models.IntegerField(u'利润', default=0)
    class Meta:
        verbose_name = '票据'
        verbose_name_plural = '票据'
    def __str__(self):
        return self.gongyingshang

class TicketsImport(models.Model):
    stamp = models.CharField(u'时间戳', max_length=100)
    pub_date = models.DateTimeField(u'导入时间', auto_now_add=True)
    piaohao = models.CharField(u'票号', max_length=100, blank=True,null=True)
    chupiaoren = models.CharField(u'出票人', max_length=100)
    shoukuanren = models.CharField(u'收款人	', max_length=100)
    piaomianjiage = models.FloatField(u'票据金额（元）	', default=0)
    piaomianlixi = models.FloatField(u'票面附带利息', default=0)
    chupiaoriqi = models.DateField(u'出票日期', )
    daoqiriqi = models.DateField(u'到期日期', )
    leixing = models.CharField(u'类型', max_length=100)
    zhuangtai = models.CharField(u'状态	', max_length=100)
    chupiaohang = models.CharField(u'出票人开户行', max_length=100)
    chupiaohangb = models.CharField(u'出票人开户行B', max_length=100)
    chengduiren = models.CharField(u'承兑人/承兑银行	', max_length=100)
    shoupiaoren = models.CharField(u'收票人账号', max_length=100)
    shoupiaohang = models.CharField(u'收票人开户行', max_length=100)
    saved = models.BooleanField(u'是否已保存', default=False)
    class Meta:
        verbose_name = '导入票据'
        verbose_name_plural = '导入票据'
    def __str__(self):
        return self.piaohao

class StoreTicketsImport(models.Model):
    stamp = models.CharField(u'时间戳', max_length=100)
    pub_date = models.DateTimeField(u'导入时间', auto_now_add=True)
    qianpaipiaohao = models.CharField(u'前排票号', max_length=100, blank=True,null=True)
    piaohao = models.CharField(u'票号', max_length=100, blank=True,null=True)
    chupiaoren = models.CharField(u'出票人', max_length=100)
    shoukuanren = models.CharField(u'收款人	', max_length=100)
    piaomianjiage = models.FloatField(u'票据金额（元）	', default=0)
    piaomianlixi = models.FloatField(u'票面附带利息', default=0)
    maipiaoriqi = models.DateField(u'购买日期', )
    chupiaoriqi = models.DateField(u'出票日期', )
    daoqiriqi = models.DateField(u'到期日期', )
    leixing = models.CharField(u'类型', max_length=100)
    zhuangtai = models.CharField(u'状态	', max_length=100)
    chupiaohang = models.CharField(u'出票人开户行', max_length=100)
    chupiaohangb = models.CharField(u'出票人开户行B', max_length=100)
    chengduiren = models.CharField(u'承兑人/承兑银行	', max_length=100)
    shoupiaoren = models.CharField(u'收票人账号', max_length=100)
    shoupiaohang = models.CharField(u'收票人开户行', max_length=100)
    saved = models.BooleanField(u'是否已保存', default=False)
    class Meta:
        verbose_name = '导入票据'
        verbose_name_plural = '导入票据'
    def __str__(self):
        return self.piaohao
class SuperLoan(BaseLoan):
    class Meta:
        verbose_name = '超短贷'
        verbose_name_plural = '超短贷'

class SuperLoanFee(models.Model):
    superloan = models.ForeignKey( SuperLoan, related_name='superloan_fee_a', verbose_name=u'超短贷' ,  blank=True,null=True)
    name = models.CharField(u'费用内容', max_length=50)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '超短贷费用'
        verbose_name_plural = '超短贷费用'

class Fee(models.Model):
    order = models.ForeignKey( Order, related_name='order_fee', verbose_name=u'订单费用' ,  blank=True,null=True)
    loanorder = models.ForeignKey( Loan_Order, related_name='loanorder_fee', verbose_name=u'借贷费用' ,  blank=True,null=True)
    superloan = models.ForeignKey( SuperLoan, related_name='superloan_fee', verbose_name=u'超短贷' ,  blank=True,null=True)
    yinhangka = models.ForeignKey( Card, related_name='fee_card', verbose_name=u'银行卡' , blank=False,null=False)
    name = models.CharField(u'费用内容', max_length=50)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    FEE_TYPE= (
        (11,u'银行卡存入'),
        (12,u'银行卡取出'),
        (13,u'银行卡转入'),
        (14,u'银行卡转出'),
        (21,u'从保证金提取'),
        (22,u'充值到保证金'),
        (31,u'还超短贷'),
        (41,u'借款给他人'),
        (42,u'从他人处贷款'),
        (411,u'从他人处预收款'),
        (422,u'预付款款给他人'),
        (43,u'收回借款本金'),
        (44,u'偿还贷款本金'),
        (45,u'收回借款费用支出'),
        (46,u'偿还贷款费用支出'),
        (47,u'收回借款费用收入'),
        (48,u'偿还贷款费用收入'),
        (49,u'收回借款利息'),
        (50,u'偿还贷款利息'),
        (51,u'偿还超短贷本金'),
        (52,u'偿还超短贷利息'),
        (1,u'付款订单'),
        (2,u'付款订单'),
        (3,u'付款支付'),
        (4,u'收款收取'),
        (5,u'付款费用支出'),
        (6,u'收款费用支出'),
        (7,u'付款费用收入'),
        (8,u'收款费用收入'),
    )
    fee_type = models.IntegerField(
        u'费用类型',
        choices=FEE_TYPE,
        default=1,
    )
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '费用'
        verbose_name_plural = '费用'


class StoreFee(models.Model):
    ticket = models.ForeignKey( Ticket, related_name='storefee_ticket', verbose_name=u'票据' ,  blank=True,null=True)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)
    create_date = models.DateField(u'添加日期', auto_now_add=True)

    STROEFEE_STATUS= (
        (1,u'入库'),
        (2,u'离库'),
    )
    storefee_status = models.IntegerField(
        u'费用内容',
        choices=STROEFEE_STATUS,
        default=1,
    )
    def __str__(self):
        return (u'%d' % (self.storefee_status))
    class Meta:
        verbose_name = '库存费用'
        verbose_name_plural = '库存费用'

class Pool(models.Model):
    create_date = models.DateField(u'添加日期', auto_now_add=True)
    totalmoney = models.FloatField(u'总额度', default=0)
    promoney = models.FloatField(u'保证金', default=0)
    loanmoney = models.FloatField(u'超短贷', default=0)
    unusemoney = models.FloatField(u'可用额度', default=0)
    usedmoney = models.FloatField(u'已用额度', default=0)
    ticket = models.ForeignKey( Ticket, related_name='pool_ticket', verbose_name=u'票据' ,  blank=True,null=True)
    card = models.ForeignKey( Card, related_name='pool_card', verbose_name=u'银行卡' ,  blank=True,null=True)
    loan = models.ForeignKey( SuperLoan, related_name='pool_loan', verbose_name=u'超短贷' ,  blank=True,null=True)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)

    POOL_STATUS= (
        (1,u'入池'),
        (2,u'出池'),
        (3,u'保证金收入'),
        (4,u'保证金支出'),
        (5,u'开票付款'),
        (6,u'新增超短贷'),
        (7,u'超短贷还款'),
        (8,u'保证金还超短贷'),
        (9,u'保证金还池开票'),
    )
    pool_status = models.IntegerField(
        u'费用内容',
        choices=POOL_STATUS,
        default=1,
    )
    def __str__(self):
        return (u'%d' % (self.pool_status))
    class Meta:
        verbose_name = '资金池'
        verbose_name_plural = '资金池'

class InpoolPercent(models.Model):
    inpoolPer = models.FloatField(u'入池额度比例', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    class Meta:
        verbose_name = '入池额度比例'
        verbose_name_plural = '入池额度比例'

    def __str__(self):
        return (u'%f' % (self.inpoolPer))

class CardTrans(models.Model):
    fromCard = models.ForeignKey( Card, related_name='tran_from_card', verbose_name=u'转出账户' , blank=False,null=False)
    money = models.FloatField(u'金额', default=0)
    toCard = models.ForeignKey( Card, related_name='tran_to_card', verbose_name=u'转入账户' , blank=False,null=False)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)

class OperLog(models.Model):
    OPER_TYPE= (
        (101,u'新建开票'),
        (102,u'新建池开票'),
        (103,u'票据入库'),
        (104,u'票据入池'),
        (105,u'票据在池到期'),
        (106,u'票据导入'),
        (201,u'新建付款'),
        (202,u'新建收款'),
        (203,u'付款'),
        (204,u'收款'),
        (301,u'新建借款'),
        (302,u'新建贷款'),
        (303,u'借款收本'),
        (304,u'借款收息'),
        (305,u'贷款还本'),
        (306,u'贷款还息'),
        (307,u'新建预收款'),
        (308,u'新建预付款'),
        (401,u'新建银行卡'),
        (402,u'银行卡存入'),
        (403,u'银行卡取出'),
        (404,u'银行卡转账'),
        (501,u'保证金存入'),
        (502,u'保证金取出'),
        (503,u'新增超短贷'),
        (504,u'超短贷还本'),
        (505,u'超短贷还息'),
        (506,u'池开票还款'),
    )
    oper_type = models.IntegerField(
        u'操作类型',
        choices=OPER_TYPE,
        default=101,
    )
    detail = models.CharField(u'相关票据卡', max_length=255, blank=False,null=False)
    contdetail = models.TextField(u'详情', blank=False,null=False)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)
    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = '操作记录'
    def __str__(self):
        return self.get_oper_type_display()