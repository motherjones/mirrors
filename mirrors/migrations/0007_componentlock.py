# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirrors', '0006_auto_20140609_2314'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locked_by', models.ForeignKey(to='auth.User', to_field='id')),
                ('locked_at', models.DateTimeField(auto_now_add=True)),
                ('lock_ends_at', models.DateTimeField()),
                ('component', models.ForeignKey(to='mirrors.Component', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
