# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentrevision',
            name='metadata',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='component',
            name='metadata',
        ),
    ]
