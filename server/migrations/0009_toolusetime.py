# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_auto_20150928_0136'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolUseTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.PositiveIntegerField()),
                ('inuseby', models.ForeignKey(to='server.User')),
                ('tool', models.ForeignKey(to='server.Tool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
