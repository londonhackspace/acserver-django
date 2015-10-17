# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0015_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='secret',
            field=models.CharField(max_length=8, null=True),
            preserve_default=True,
        ),
    ]
