# Generated by Django 3.0.5 on 2020-05-11 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn_word', '0015_auto_20200509_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='englishword',
            name='order',
        ),
        migrations.AlterField(
            model_name='englishword',
            name='word',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
