# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0008_auto_20140814_2150')
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]
