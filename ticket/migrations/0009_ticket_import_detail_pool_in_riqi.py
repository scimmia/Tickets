# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-24 15:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0008_ticket_import_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket_import_detail',
            name='pool_in_riqi',
            field=models.DateTimeField(blank=True, null=True, verbose_name='入池日期'),
        ),
    ]
