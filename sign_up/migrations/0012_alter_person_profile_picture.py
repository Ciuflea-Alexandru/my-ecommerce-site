# Generated by Django 5.0.3 on 2024-05-04 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign_up', '0011_alter_person_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
