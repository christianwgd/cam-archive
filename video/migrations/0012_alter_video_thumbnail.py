# Generated by Django 5.1.6 on 2025-03-01 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0011_alter_video_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='thumbnail',
            field=models.FileField(blank=True, null=True, upload_to='thumbs/', verbose_name='thumbnail'),
        ),
    ]
