# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0004_auto_20140609_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentrevision',
            name='metadata',
            field=jsonfield.fields.JSONField(default=None, null=True),
        ),
    ]
