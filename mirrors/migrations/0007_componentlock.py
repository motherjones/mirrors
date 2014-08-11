# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mirrors', '0006_auto_20140609_2314'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locked_at', models.DateTimeField(auto_now_add=True)),
                ('lock_ends_at', models.DateTimeField()),
                ('broken', models.BooleanField(default=False)),
                ('component', models.ForeignKey(to='mirrors.Component')),
                ('locked_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
