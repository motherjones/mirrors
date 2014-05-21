# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0002_componentlock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentlock',
            name='locked_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id'),
        ),
    ]
