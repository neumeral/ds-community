# Generated by Django 3.1.7 on 2022-06-18 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dshunt', '0002_auto_20220619_0225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('dshunt.post',),
        ),
        migrations.CreateModel(
            name='PodcastEpisode',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('dshunt.post',),
        ),
        migrations.CreateModel(
            name='Tutorial',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('dshunt.post',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('dshunt.post',),
        ),
    ]