# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_djacuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DJACUser',
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['id'], 'verbose_name': 'ACNode User'},
        ),
    ]
