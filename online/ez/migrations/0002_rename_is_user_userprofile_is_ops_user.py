# Generated by Django 4.1.3 on 2023-12-16 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ez', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_user',
            new_name='is_ops_user',
        ),
    ]
