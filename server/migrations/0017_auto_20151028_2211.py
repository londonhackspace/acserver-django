# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0016_tool_secret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
