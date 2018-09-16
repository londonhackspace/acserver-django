# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_id', models.CharField(unique=True, max_length=15, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('message', models.TextField()),
                ('time', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.PositiveIntegerField(choices=[(1, b'user'), (2, b'maintainer')])),
                ('date', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('status', models.PositiveIntegerField(default=0, choices=[(1, b'Operational'), (0, b'Out of service')])),
                ('status_message', models.TextField()),
                ('inuse', models.BooleanField(default=False, choices=[(True, b'yes'), (False, b'no')])),
                ('secret', models.CharField(max_length=8, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ToolUseTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('subscribed', models.BooleanField(default=False, choices=[(True, b'Subscribed'), (False, b'Not Subscribed')])),
            ],
            options={
                'verbose_name': 'ACNode User',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('id', 'name')]),
        ),
        migrations.AddField(
            model_name='toolusetime',
            name='inuseby',
            field=models.ForeignKey(to='server.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='toolusetime',
            name='tool',
            field=models.ForeignKey(to='server.Tool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, to='server.User', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permissions',
            name='addedby',
            field=models.ForeignKey(related_name='addedpermissions', to='server.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permissions',
            name='tool',
            field=models.ForeignKey(to='server.Tool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permissions',
            name='user',
            field=models.ForeignKey(to='server.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='permissions',
            unique_together=set([('user', 'tool')]),
        ),
        migrations.AddField(
            model_name='log',
            name='tool',
            field=models.ForeignKey(to='server.Tool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(to='server.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='user',
            field=models.ForeignKey(to='server.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
