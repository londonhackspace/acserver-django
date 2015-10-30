# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0018_auto_20151029_0053'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='time',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='permissions',
            name='date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
