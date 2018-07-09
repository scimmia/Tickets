# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-09 10:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0030_superloanfee_fee_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='superloanfee',
            name='fee_type',
        ),
        migrations.RemoveField(
            model_name='superloanfee',
            name='ispoolpay',
        ),
        migrations.RemoveField(
            model_name='superloanfee',
            name='yinhangka',
        ),
        migrations.AddField(
            model_name='fee',
            name='superloan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='superloan_fee', to='ticket.SuperLoan', verbose_name='超短贷'),
        ),
        migrations.AlterField(
            model_name='fee',
            name='fee_type',
            field=models.IntegerField(choices=[(11, '银行卡存入'), (12, '银行卡取出'), (21, '从保证金提取'), (22, '充值到保证金'), (31, '还超短贷'), (41, '借款给他人'), (42, '从他人处贷款'), (43, '收回借款本金'), (44, '偿还贷款本金'), (45, '收回借款费用支出'), (46, '偿还贷款费用支出'), (47, '收回借款费用收入'), (48, '偿还贷款费用收入'), (49, '收回借款利息'), (50, '偿还贷款利息'), (51, '偿还超短贷本金'), (52, '偿还超短贷利息'), (1, '付款订单'), (2, '付款订单'), (3, '付款支付'), (4, '收款收取'), (5, '付款费用支出'), (6, '收款费用支出'), (7, '付款费用收入'), (8, '收款费用收入')], default=1, verbose_name='费用类型'),
        ),
        migrations.AlterField(
            model_name='superloanfee',
            name='name',
            field=models.CharField(default=1, max_length=50, verbose_name='费用内容'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='superloanfee',
            name='superloan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='superloan_fee_a', to='ticket.SuperLoan', verbose_name='超短贷'),
        ),
    ]
