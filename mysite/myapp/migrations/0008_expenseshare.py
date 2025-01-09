# Generated by Django 5.1.4 on 2024-12-28 20:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_expense_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expsAmount', models.FloatField()),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.expense')),
                ('expsPerson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.person')),
            ],
        ),
    ]
