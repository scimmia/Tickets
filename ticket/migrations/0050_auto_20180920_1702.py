# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-09-20 17:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0049_feedetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyWithCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='金额')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='money_card', to='ticket.Card', verbose_name='银行卡')),
            ],
        ),
        migrations.AlterField(
            model_name='feedetail',
            name='fee_type',
            field=models.IntegerField(choices=[(101, '新建开票'), (102, '新建池开票'), (103, '票据入库'), (104, '票据入池'), (105, '票据在池到期'), (106, '票据导入'), (201, '新建付款'), (202, '新建收款'), (203, '付款'), (204, '收款'), (301, '新建借款'), (302, '新建贷款'), (303, '借款收本'), (304, '借款收息'), (305, '贷款还本'), (306, '贷款还息'), (307, '新建预收款'), (308, '新建预付款'), (401, '新建银行卡'), (402, '银行卡存入'), (403, '银行卡取出'), (404, '银行卡转账'), (501, '保证金存入'), (502, '保证金取出'), (503, '新增超短贷'), (504, '超短贷还本'), (505, '超短贷还息'), (506, '池开票还款'), (507, '超短贷结息')], default=1, verbose_name='费用类型'),
        ),
        migrations.AlterField(
            model_name='operlog',
            name='oper_type',
            field=models.IntegerField(choices=[(101, '新建开票'), (102, '新建池开票'), (103, '票据入库'), (104, '票据入池'), (105, '票据在池到期'), (106, '票据导入'), (201, '新建付款'), (202, '新建收款'), (203, '付款'), (204, '收款'), (301, '新建借款'), (302, '新建贷款'), (303, '借款收本'), (304, '借款收息'), (305, '贷款还本'), (306, '贷款还息'), (307, '新建预收款'), (308, '新建预付款'), (401, '新建银行卡'), (402, '银行卡存入'), (403, '银行卡取出'), (404, '银行卡转账'), (501, '保证金存入'), (502, '保证金取出'), (503, '新增超短贷'), (504, '超短贷还本'), (505, '超短贷还息'), (506, '池开票还款'), (507, '超短贷结息')], default=101, verbose_name='操作类型'),
        ),
    ]
