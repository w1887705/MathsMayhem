from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_progress_steps"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add stars to Progress
        migrations.AddField(
            model_name="progress",
            name="stars",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        # UserProfile
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("total_stars", models.PositiveIntegerField(default=0)),
                ("user", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        # ShopItem
        migrations.CreateModel(
            name="ShopItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("cost", models.PositiveIntegerField(default=1)),
                ("emoji", models.CharField(default="🎁", max_length=10)),
                ("is_available", models.BooleanField(default=True)),
            ],
        ),
        # UserShopItem
        migrations.CreateModel(
            name="UserShopItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("purchased_at", models.DateTimeField(auto_now_add=True)),
                ("item", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to="core.shopitem",
                )),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"unique_together": {("user", "item")}},
        ),
    ]
