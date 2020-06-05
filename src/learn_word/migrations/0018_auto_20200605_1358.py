# Generated by Django 3.0.5 on 2020-06-05 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn_word', '0017_auto_20200512_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordlearnsetting',
            name='is_random',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wordlearnsetting',
            name='is_shuffle',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='wordlearnsetting',
            name='show_oxford_mean',
            field=models.BooleanField(default=False),
        ),
    ]
