# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_auto_20150928_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='permissions',
            unique_together=set([('user', 'tool')]),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('id', 'name')]),
        ),
    ]
