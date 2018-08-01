# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0007_djacuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='permission',
            field=models.PositiveIntegerField(choices=[(1, 'user'), (2, 'maintainer')]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(choices=[(True, 'yes'), (False, 'no')], default=False),
        ),
        migrations.AlterField(
            model_name='tool',
            name='secret',
            field=models.CharField(help_text='The shared secret to use with the acnode, only for version 0.8 or better acnodes', max_length=8, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='tool',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Operational'), (0, 'Out of service')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscribed',
            field=models.BooleanField(choices=[(True, 'Subscribed'), (False, 'Not Subscribed')], default=False),
        ),
    ]
