# Generated by Django 5.1.6 on 2025-02-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_alter_video_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FilePathField(path='test_videos/', verbose_name='Video file'),
        ),
    ]
