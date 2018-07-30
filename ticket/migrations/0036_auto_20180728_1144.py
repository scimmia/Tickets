# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-28 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0035_operlog_operlogcont'),
    ]

    operations = [
        migrations.AddField(
            model_name='operlog',
            name='contdetail',
            field=models.TextField(default='qw', verbose_name='详情'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='operlog',
            name='detail',
            field=models.CharField(default='1', max_length=255, verbose_name='相关票据卡'),
            preserve_default=False,
        ),
    ]
