# Generated by Django 5.0.6 on 2024-06-29 00:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0008_remove_test_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="test",
            name="link",
            field=models.URLField(blank=True, null=True),
        ),
    ]
