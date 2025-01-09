# Generated by Django 5.1.4 on 2024-12-26 18:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='image',
            field=models.ImageField(default='static/images/uses/default-1.png', upload_to='static/images/users'),
        ),
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupName', models.CharField(max_length=100)),
                ('made_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Group_creator', to='myapp.person')),
                ('members', models.ManyToManyField(related_name='group_members', to='myapp.person')),
            ],
        ),
    ]