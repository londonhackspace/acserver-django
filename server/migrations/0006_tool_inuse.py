# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
