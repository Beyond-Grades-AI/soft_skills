# Generated by Django 5.0.6 on 2024-06-12 12:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0006_alter_test_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="test",
            name="date",
            field=models.CharField(max_length=100),
        ),
    ]