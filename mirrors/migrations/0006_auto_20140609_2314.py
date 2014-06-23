# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0005_auto_20140609_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentrevision',
            name='metadata',
            field=jsonfield.fields.JSONField(default=None, null=True, blank=True),
        ),
    ]
