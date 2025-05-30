# Generated by Django 5.1.6 on 2025-04-22 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_receipt_receipt_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='reset_token',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='reset_token_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
