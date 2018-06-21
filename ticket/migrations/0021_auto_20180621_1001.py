# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0020_auto_20180620_1649'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_type', models.IntegerField(choices=[(3, '借款订单'), (4, '贷款订单')], default=3, verbose_name='订单类型')),
                ('jiedairen', models.CharField(max_length=100, verbose_name='借贷人')),
                ('money_benjin', models.FloatField(default=0, verbose_name='本金')),
                ('money_lixi', models.FloatField(default=0, verbose_name='利息')),
                ('money_total', models.FloatField(default=0, verbose_name='应收付金额')),
                ('payfee_sum', models.FloatField(default=0, verbose_name='已支付金额')),
                ('payfee_count', models.IntegerField(default=0, verbose_name='已支付数目')),
                ('total_sum', models.FloatField(default=0, verbose_name='总金额')),
                ('needpay_sum', models.FloatField(default=0, verbose_name='剩余金额')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='添加日期')),
                ('yinhangka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loanorder_card', to='ticket.Card', verbose_name='借贷卡')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
            },
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.IntegerField(choices=[(1, '付款订单'), (2, '收款订单')], default=1, verbose_name='订单类型'),
        ),
        migrations.AlterField(
            model_name='pool',
            name='pool_status',
            field=models.IntegerField(choices=[(1, '入池'), (2, '出池'), (3, '保证金收入'), (4, '保证金支出'), (5, '开票付款'), (6, '新增超短贷'), (7, '超短贷还款'), (8, '保证金还超短贷')], default=1, verbose_name='费用内容'),
        ),
    ]
