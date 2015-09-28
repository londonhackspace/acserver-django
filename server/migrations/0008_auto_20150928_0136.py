# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0007_tool_inuseby'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, to='server.User', null=True),
            preserve_default=True,
        ),
    ]
