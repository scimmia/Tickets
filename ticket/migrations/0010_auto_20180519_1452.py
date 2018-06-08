# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-19 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0009_fee_fee_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='moneyleft',
            new_name='needpay_sum',
        ),
        migrations.AddField(
            model_name='order',
            name='fee_count',
            field=models.FloatField(default=0, verbose_name='合计费用金额'),
        ),
        migrations.AddField(
            model_name='order',
            name='fee_sum',
            field=models.FloatField(default=0, verbose_name='费用数目'),
        ),
        migrations.AddField(
            model_name='order',
            name='payfee_count',
            field=models.FloatField(default=0, verbose_name='已支付金额'),
        ),
        migrations.AddField(
            model_name='order',
            name='payfee_sum',
            field=models.FloatField(default=0, verbose_name='已支付数目'),
        ),
        migrations.AddField(
            model_name='order',
            name='ticket_count',
            field=models.FloatField(default=0, verbose_name='合计票面价格'),
        ),
        migrations.AddField(
            model_name='order',
            name='ticket_sum',
            field=models.FloatField(default=0, verbose_name='票据数目'),
        ),
        migrations.AddField(
            model_name='order',
            name='total_sum',
            field=models.FloatField(default=0, verbose_name='总金额'),
        ),
    ]