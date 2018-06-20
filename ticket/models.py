from django.db import models

# Create your models here.

class Card(models.Model):
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
        (3,u'付款订单'),
        (4,u'收款订单'),
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
        return self.order_type

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

class Fee(models.Model):
    order = models.ForeignKey( Order, related_name='order_fee', verbose_name=u'订单费用' ,  blank=True,null=True)
    yinhangka = models.ForeignKey( Card, related_name='fee_card', verbose_name=u'银行卡' , blank=False,null=False)
    name = models.CharField(u'费用内容', max_length=50)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    FEE_TYPE= (
        (11,u'银行卡存入'),
        (12,u'银行卡取出'),
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

class PoolFee(models.Model):
    ticket = models.ForeignKey( Ticket, related_name='poolfee_ticket', verbose_name=u'票据' ,  blank=True,null=True)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)
    create_date = models.DateField(u'添加日期', auto_now_add=True)

    POOLFEE_STATUS= (
        (1,u'入池'),
        (2,u'出池'),
        (5,u'保证金'),
    )
    poolfee_status = models.IntegerField(
        u'费用内容',
        choices=POOLFEE_STATUS,
        default=1,
    )
    def __str__(self):
        return self.poolfee_status
    class Meta:
        verbose_name = '资金池费用'
        verbose_name_plural = '资金池费用'
class SuperLoan(models.Model):
    name = models.CharField(u'贷款内容', max_length=50)
    money = models.FloatField(u'金额', default=0)
    ispoolrepay = models.BooleanField(u'是否保证金还款',default=False)
    yinhangka = models.ForeignKey( Card, related_name='loan_card', verbose_name=u'还款银行卡' , blank=True,null=True)
    isfinished = models.BooleanField(u'是否还清',default=False)
    repay_date = models.DateTimeField(u'还款日期', blank=True,null=True)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '超短贷'
        verbose_name_plural = '超短贷'

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
        return self.storefee_status
    class Meta:
        verbose_name = '库存费用'
        verbose_name_plural = '库存费用'

class Pool(models.Model):
    create_date = models.DateField(u'添加日期', auto_now_add=True)
    totalmoney = models.FloatField(u'总额度', default=0)
    promoney = models.FloatField(u'保证金', default=0)
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
    )
    pool_status = models.IntegerField(
        u'费用内容',
        choices=POOL_STATUS,
        default=1,
    )
    def __str__(self):
        return self.pool_status
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
        return self.inpoolPer