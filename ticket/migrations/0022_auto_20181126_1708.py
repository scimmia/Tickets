# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-26 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0021_auto_20181126_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan_order',
            name='lilv',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name=' '),
        ),
        migrations.AlterField(
            model_name='poollicai',
            name='lilv',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='利率'),
        ),
        migrations.AlterField(
            model_name='superloan',
            name='lilv',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name=' '),
        ),
    ]