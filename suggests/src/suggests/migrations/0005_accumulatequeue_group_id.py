# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggests', '0004_auto_20170503_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='accumulatequeue',
            name='group_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
