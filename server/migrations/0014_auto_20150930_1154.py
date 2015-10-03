# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_auto_20150928_1759'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'ACNode User'},
        ),
        migrations.AddField(
            model_name='permissions',
            name='addedby',
            field=models.ForeignKey(related_name='addedpermissions', default=1, to='server.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permissions',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 30, 11, 54, 52, 729078, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, to='server.User', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='subscribed',
            field=models.BooleanField(default=False, choices=[(True, b'Subscribed'), (False, b'Not Subscribed')]),
            preserve_default=True,
        ),
    ]
