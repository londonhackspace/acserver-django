# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20150927_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='subscribed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
