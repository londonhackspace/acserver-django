# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0014_auto_20150930_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('message', models.TextField()),
                ('tool', models.ForeignKey(to='server.Tool')),
                ('user', models.ForeignKey(to='server.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
