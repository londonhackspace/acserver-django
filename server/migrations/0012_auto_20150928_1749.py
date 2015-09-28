# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0011_auto_20150928_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='card_id',
            field=models.CharField(unique=True, max_length=15, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, editable=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, editable=False, to='server.User', null=True),
            preserve_default=True,
        ),
    ]
