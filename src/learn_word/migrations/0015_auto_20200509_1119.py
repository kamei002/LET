# Generated by Django 3.0.5 on 2020-05-09 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn_word', '0014_auto_20200509_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordlearnsetting',
            name='show_mean',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='wordlearnsetting',
            name='show_oxford_mean',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='wordlearnsetting',
            name='show_synonyms',
            field=models.BooleanField(default=True),
        ),
    ]
