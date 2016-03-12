# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('server', '0006_auto_20160218_0059'),
    ]

    operations = [
        migrations.CreateModel(
            name='DJACUser',
            fields=[
            ],
            options={
                'verbose_name': 'User',
                'proxy': True,
            },
            bases=('auth.user',),
        ),
    ]
