# Generated by Django 3.0.5 on 2020-04-22 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EnglishWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('is_checked', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_displayed_at', models.DateTimeField(default=django.utils.timezone.now, null=True)),
            ],
            options={
                'db_table': 'english_word',
            },
        ),
        migrations.CreateModel(
            name='WordMeaning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meaning', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('english_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learn_word.EnglishWord')),
            ],
            options={
                'db_table': 'word_meaning',
            },
        ),
        migrations.CreateModel(
            name='WordLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_unknown', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('english_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_logs', to='learn_word.EnglishWord')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'word_log',
            },
        ),
        migrations.CreateModel(
            name='WordLearnSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_num', models.IntegerField(default=10)),
                ('default_unknown', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'word_learning_setting',
            },
        ),
        migrations.CreateModel(
            name='WordCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='learn_word.WordCategory')),
            ],
            options={
                'db_table': 'word_category',
            },
        ),
        migrations.CreateModel(
            name='WordAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=255)),
                ('english_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_audios', to='learn_word.EnglishWord')),
            ],
            options={
                'db_table': 'word_audio',
            },
        ),
        migrations.AddField(
            model_name='englishword',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='word_audios', to='learn_word.WordCategory'),
        ),
        migrations.AddField(
            model_name='englishword',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
