# Generated by Django 5.1.6 on 2025-02-28 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0006_video_camera'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Video', 'verbose_name_plural': 'Videos'},
        ),
    ]
