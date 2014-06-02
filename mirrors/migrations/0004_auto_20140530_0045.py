# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0003_remove_component_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentrevision',
            name='data',
            field=models.BinaryField(null=True, editable=False),
        ),
    ]
