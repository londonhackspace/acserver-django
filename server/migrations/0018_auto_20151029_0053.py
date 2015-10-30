# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0017_auto_20151028_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissions',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
