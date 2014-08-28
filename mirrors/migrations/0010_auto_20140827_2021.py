# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mirrors.models


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0009_auto_20140825_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='month',
            field=models.IntegerField(default=0, validators=[mirrors.models.validate_is_month]),
        ),
        migrations.AlterField(
            model_name='component',
            name='year',
            field=models.IntegerField(default=0, validators=[mirrors.models.validate_is_year]),
        ),
    ]
