# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-08 01:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('map_app', '0002_usertokens'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Place',
        ),
        migrations.AlterField(
            model_name='usertokens',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
