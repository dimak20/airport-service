# Generated by Django 5.1.1 on 2024-10-06 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("air_service", "0004_airplane_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="notification_sent",
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
