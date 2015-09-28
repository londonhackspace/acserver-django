# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0006_tool_inuse'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(to='server.User', null=True),
            preserve_default=True,
        ),
    ]
