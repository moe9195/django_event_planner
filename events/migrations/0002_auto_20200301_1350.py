# Generated by Django 2.2.5 on 2020-03-01 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='follows',
            field=models.ManyToManyField(default=None, related_name='followed_by', to='events.Profile'),
        ),
    ]
