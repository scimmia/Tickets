# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-26 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0022_auto_20181126_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_collect_acctive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='is_pay_acctive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='card',
            name='name',
            field=models.CharField(max_length=50, verbose_name='名称'),
        ),
    ]
