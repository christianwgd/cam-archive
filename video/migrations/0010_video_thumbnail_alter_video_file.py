# Generated by Django 5.1.6 on 2025-03-01 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0009_alter_video_camera'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail',
            field=models.FileField(default=2, upload_to='thumbnails/', verbose_name='thumbnail'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FileField(upload_to='videos/', verbose_name='video file'),
        ),
    ]
