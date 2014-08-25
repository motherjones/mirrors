# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0009_auto_20140825_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]
