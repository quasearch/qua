# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggests', '0005_accumulatequeue_group_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accumulatequeue',
            name='last',
            field=models.IntegerField(default=-1),
        ),
    ]