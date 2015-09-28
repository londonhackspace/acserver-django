# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0010_auto_20150928_0333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(1, b'Operational'), (0, b'Out of service')]),
            preserve_default=True,
        ),
    ]
