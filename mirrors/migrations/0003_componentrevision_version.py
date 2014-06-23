# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0002_auto_20140609_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentrevision',
            name='version',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
