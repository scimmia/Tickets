# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-19 15:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_auto_20181017_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='need_pay_benjin',
            field=models.FloatField(default=0, verbose_name='应付本金'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='pool_buy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='t_pool_buy', to='ticket.Pool', verbose_name='资金池购入'),
        ),
    ]
