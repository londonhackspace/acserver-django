# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_auto_20150927_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='card_id',
            field=models.CharField(max_length=15, db_index=True),
            preserve_default=True,
        ),
    ]
