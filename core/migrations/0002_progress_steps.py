from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="progress",
            name="current_step",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="progress",
            name="total_steps",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
