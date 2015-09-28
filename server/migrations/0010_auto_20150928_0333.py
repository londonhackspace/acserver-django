# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0009_toolusetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissions',
            name='permission',
            field=models.PositiveIntegerField(choices=[(1, b'user'), (2, b'maintainer')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
    ]
