# Generated by Django 5.2.1 on 2025-05-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0013_video_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
            ],
            options={
                'verbose_name': 'Ring',
                'verbose_name_plural': 'Rings',
                'ordering': ['timestamp'],
            },
        ),
    ]
