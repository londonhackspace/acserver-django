# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_auto_20151030_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.PositiveIntegerField(choices=[(1, b'user'), (2, b'maintainer')])),
                ('date', models.DateTimeField()),
                ('addedby', models.ForeignKey(related_name='addedpermission', to='server.User')),
                ('tool', models.ForeignKey(to='server.Tool')),
                ('user', models.ForeignKey(to='server.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='permissions',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='permissions',
            name='addedby',
        ),
        migrations.RemoveField(
            model_name='permissions',
            name='tool',
        ),
        migrations.RemoveField(
            model_name='permissions',
            name='user',
        ),
        migrations.DeleteModel(
            name='Permissions',
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together=set([('user', 'tool')]),
        ),
    ]
