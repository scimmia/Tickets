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
        (5,u'入池'),
        (3, u'卖出'),
    )
    t_status = models.IntegerField(
        u'状态',
        choices=TICKET_STATUS,
        default=1,
    )
    goumairiqi = models.DateTimeField(u'购买日期', auto_now_add=True)
    qianpaipiaohao = models.CharField(u'前排票号', max_length=100, blank=True,null=True)
    piaohao = models.CharField(u'票号', max_length=100, blank=True,null=True)
    chupiaohang = models.CharField(u'出票行', max_length=100)
    chupiaoriqi = models.DateField(u'出票日期', )
    daoqiriqi = models.DateField(u'到期日期', )
    piaomianjiage = models.FloatField(u'票面价格', default=0)
    gouruhuilv = models.FloatField(u'购入利率', default=0)
    gourujiage = models.FloatField(u'购入价格', default=0)
    gouruzijinchi = models.BooleanField(u'资金池购入', default=False)
    gourucard = models.ForeignKey( Card, related_name='buy_card', verbose_name=u'购入卡' ,  blank=True,null=True)
    gongyingshang = models.CharField(u'供应商', max_length=100)
    pay_status = models.IntegerField(
        u'状态',
        choices=PAY_STATUS,
        default=1,
    )
    paytime = models.DateTimeField(u'付款时间', blank=True,null=True)
    maichuriqi = models.DateTimeField(u'卖出日期', blank=True,null=True)
    maichulilv = models.FloatField(u'卖出利率', default=0)
    maichujiage = models.FloatField(u'卖出价格', default=0)
    maichucard = models.ForeignKey( Card, related_name='sold_card',  verbose_name=u'卖出卡' ,  blank=True,null=True)
    maipiaoren = models.CharField(u'买票人', max_length=100, blank=True,null=True)
    sell_status = models.IntegerField(
        u'状态',
        choices=SELL_STATUS,
        default=1,
    )
    selltime = models.DateTimeField(u'收款时间', blank=True,null=True)
    lirun = models.IntegerField(u'利润', default=0)
    class Meta:
        verbose_name = '票据'
        verbose_name_plural = '票据'
    def __str__(self):
        return self.gongyingshang


class Fee(models.Model):
    ticket = models.ForeignKey( Ticket, related_name='fee_ticket', verbose_name=u'票据' ,  blank=True,null=True)
    yinhangka = models.ForeignKey( Card, related_name='fee_card', verbose_name=u'银行卡' , blank=False,null=False)
    name = models.CharField(u'费用内容', max_length=50)
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加日期', auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '费用'
        verbose_name_plural = '费用'

class TicketStatus(models.Model):
    TICKET_STATUS= (
        (1,u'在库'),
        (3,u'卖出'),
        (5,u'入池'),
    )
    ticket = models.ForeignKey( Ticket, related_name='status_ticket', verbose_name=u'票据')
    t_status = models.IntegerField(
        u'状态',
        choices=TICKET_STATUS,
        default=1,
    )
    pub_date = models.DateTimeField(u'登记时间', auto_now_add=True)
    #登记人
    status_signer = models.CharField(u'登记人',max_length=30,default='system')
    def __str__(self):
        return self.pub_date
    class Meta:
        verbose_name = '票据状态'
        verbose_name_plural = '票据状态'

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
    money = models.FloatField(u'金额', default=0)
    pub_date = models.DateTimeField(u'添加时间', auto_now_add=True)

    POOL_STATUS= (
        (1,u'入池'),
        (2,u'出池'),
        (3,u'保证金收入'),
        (4,u'保证金支出'),
        (5,u'开票付款'),
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