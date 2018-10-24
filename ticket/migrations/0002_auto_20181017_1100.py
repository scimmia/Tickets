# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-17 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoolPercent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=50, verbose_name='标签')),
                ('inpoolPer', models.FloatField(default=0, verbose_name='入池额度比例')),
                ('is_active', models.BooleanField(default=True, verbose_name='激活')),
                ('pool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='percent_pool', to='ticket.Pool', verbose_name='资金池')),
            ],
        ),
        migrations.CreateModel(
            name='PoolPercentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inpoolPer', models.FloatField(default=0, verbose_name='入池额度比例')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='添加日期')),
                ('inpoolPercent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pool_loan', to='ticket.PoolPercent', verbose_name='超短贷')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='poolpercent',
            unique_together=set([('pool', 'tags')]),
        ),
    ]