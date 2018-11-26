# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-26 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0018_auto_20181126_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='cardtrans',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='need_collect_benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应收本金'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='need_collect_lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应收利息'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='need_pay_benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应付本金'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='need_pay_lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应付利息'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='yufu_benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='预付本金'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='yufu_lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='预付利息'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='yushou_benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='预收本金'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='yushou_lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='预收利息'),
        ),
        migrations.AlterField(
            model_name='feedetail',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='本金'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='benjin_needpay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='待还本金'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='benjin_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='已还本金'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='lilv',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利率'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利息'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='lixi_needpay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='待还利息'),
        ),
        migrations.AlterField(
            model_name='loan_order',
            name='lixi_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='已还利息'),
        ),
        migrations.AlterField(
            model_name='moneywithcard',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='moneywithcardpool',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='order',
            name='fee_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='合计费用金额'),
        ),
        migrations.AlterField(
            model_name='order',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='合计应收付金额'),
        ),
        migrations.AlterField(
            model_name='order',
            name='needpay_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='剩余金额'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payfee_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='已支付金额'),
        ),
        migrations.AlterField(
            model_name='order',
            name='ticket_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='合计票面价格'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='总金额'),
        ),
        migrations.AlterField(
            model_name='per_detail',
            name='money',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='poollicai',
            name='benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='本金'),
        ),
        migrations.AlterField(
            model_name='poollicai',
            name='lilv',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利率'),
        ),
        migrations.AlterField(
            model_name='poollicai',
            name='lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利息'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='benjin',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='本金'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='benjin_needpay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='待还本金'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='benjin_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='已还本金'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='lilv',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利率'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='lixi',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='利息'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='lixi_needpay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='待还利息'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='lixi_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='已还利息'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='gourujiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='购入价格'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='maichujiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='卖出价格'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='piaomianjiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='票面价格(元)'),
        ),
        migrations.AlterField(
            model_name='ticket_import_detail',
            name='gourujiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='购入价格'),
        ),
        migrations.AlterField(
            model_name='ticket_import_detail',
            name='maichujiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='卖出价格'),
        ),
        migrations.AlterField(
            model_name='ticket_import_detail',
            name='piaomianjiage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='票面价格(元)'),
        ),
    ]
