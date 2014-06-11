# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0002_auto_20140529_2023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='component',
            name='metadata',
        ),
    ]
