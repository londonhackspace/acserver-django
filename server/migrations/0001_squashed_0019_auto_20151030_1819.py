# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'server', '0001_initial'), (b'server', '0002_auto_20150927_2010'), (b'server', '0003_auto_20150927_2018'), (b'server', '0004_user_subscribed'), (b'server', '0005_permissions'), (b'server', '0006_tool_inuse'), (b'server', '0007_tool_inuseby'), (b'server', '0008_auto_20150928_0136'), (b'server', '0009_toolusetime'), (b'server', '0010_auto_20150928_0333'), (b'server', '0011_auto_20150928_1153'), (b'server', '0012_auto_20150928_1749'), (b'server', '0013_auto_20150928_1759'), (b'server', '0014_auto_20150930_1154'), (b'server', '0015_log'), (b'server', '0016_tool_secret'), (b'server', '0017_auto_20151028_2211'), (b'server', '0018_auto_20151029_0053'), (b'server', '0019_auto_20151030_1819')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('status', models.PositiveIntegerField()),
                ('status_message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_id', models.CharField(max_length=15)),
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
                ('subscribed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='card',
            name='user',
            field=models.ForeignKey(to='server.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='card_id',
            field=models.CharField(max_length=15, db_index=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.PositiveIntegerField(choices=[(1, b'user'), (2, b'maintainer')])),
                ('tool', models.ForeignKey(to='server.Tool')),
                ('user', models.ForeignKey(to='server.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, to='server.User', null=True),
            preserve_default=True,
        ),
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
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(1, b'Operational'), (0, b'Out of service')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='card_id',
            field=models.CharField(unique=True, max_length=15, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, editable=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, editable=False, to='server.User', null=True),
            preserve_default=True,
        ),
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
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'ACNode User'},
        ),
        migrations.AddField(
            model_name='permissions',
            name='addedby',
            field=models.ForeignKey(related_name='addedpermissions', default=1, to='server.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permissions',
            name='date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuse',
            field=models.BooleanField(default=False, choices=[(True, b'yes'), (False, b'no')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tool',
            name='inuseby',
            field=models.ForeignKey(default=None, to='server.User', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='subscribed',
            field=models.BooleanField(default=False, choices=[(True, b'Subscribed'), (False, b'Not Subscribed')]),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('message', models.TextField()),
                ('tool', models.ForeignKey(to='server.Tool')),
                ('user', models.ForeignKey(to='server.User')),
                ('time', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tool',
            name='secret',
            field=models.CharField(max_length=8, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
