from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_stars_shop"),
    ]

    operations = [
        migrations.AddField(
            model_name="progress",
            name="easy_stars",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="progress",
            name="medium_stars",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="progress",
            name="hard_stars",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
