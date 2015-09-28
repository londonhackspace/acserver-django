# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_user_subscribed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.PositiveIntegerField(choices=[(1, b'User'), (2, b'Maintainer')])),
                ('tool', models.ForeignKey(to='server.Tool')),
                ('user', models.ForeignKey(to='server.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
