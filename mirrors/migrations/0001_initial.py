# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=100)),
                ('metadata', jsonfield.fields.JSONField(default={})),
                ('content_type', models.CharField(default='none', max_length=50)),
                ('schema_name', models.CharField(max_length=50, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent', models.ForeignKey(to='mirrors.Component', to_field='id')),
                ('child', models.ForeignKey(to='mirrors.Component', to_field='id')),
                ('name', models.CharField(max_length=255)),
                ('weight', models.IntegerField(default=-1)),
                ('added_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.BinaryField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(to='mirrors.Component', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
