# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mirrors.models


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0008_auto_20140814_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='month',
            field=mirrors.models.MonthField(default=0),
        ),
        migrations.AlterField(
            model_name='component',
            name='year',
            field=mirrors.models.YearField(default=0),
        ),
    ]
