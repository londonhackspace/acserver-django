# Generated by Django 3.2.25 on 2024-11-30 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_alter_tool_mqtt_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ldap',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]
