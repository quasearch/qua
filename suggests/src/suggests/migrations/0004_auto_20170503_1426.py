# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggests', '0003_auto_20170502_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='accumulatequeue',
            name='freq',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='accumulatequeue',
            name='last',
            field=models.IntegerField(default=1),
        ),
    ]
