# Generated by Django 5.1.4 on 2024-12-26 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_person_image_alter_person_name_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='groupName',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
