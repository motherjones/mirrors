# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0007_componentlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentlock',
            name='broken',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
