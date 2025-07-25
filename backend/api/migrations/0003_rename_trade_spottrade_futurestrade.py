# Generated by Django 5.2.4 on 2025-07-25 20:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_rename_excnahge_trade_exchange"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Trade",
            new_name="SpotTrade",
        ),
        migrations.CreateModel(
            name="FuturesTrade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("symbol", models.CharField(max_length=10)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("entry_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "liquidation_price",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("leverage", models.IntegerField()),
                (
                    "pnl",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("exchange", models.CharField(max_length=20)),
                ("amount", models.DecimalField(decimal_places=8, max_digits=20)),
                ("trade_time", models.DateTimeField(auto_now_add=True)),
                (
                    "side",
                    models.CharField(
                        choices=[("BUY", "Buy"), ("SELL", "Sell")], max_length=4
                    ),
                ),
                ("currency", models.CharField(max_length=20)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
