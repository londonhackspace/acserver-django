# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20151105_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='secret',
            field=models.CharField(default=b'', help_text=b'The shared secret to use with the acnode, only for version 0.8 or better acnodes', max_length=8, blank=True),
            preserve_default=True,
        ),
    ]
