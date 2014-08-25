# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0007_componentlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='month',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='component',
            name='year',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='component',
            unique_together=set([('slug', 'year', 'month')]),
        ),
        migrations.AlterIndexTogether(
            name='component',
            index_together=set([('slug', 'year', 'month')]),
        ),
    ]
