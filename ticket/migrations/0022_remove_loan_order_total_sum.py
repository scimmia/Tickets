# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 10:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0021_auto_20180621_1001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan_order',
            name='total_sum',
        ),
    ]