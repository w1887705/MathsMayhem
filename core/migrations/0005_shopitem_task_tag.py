from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0004_per_diff_stars")]

    operations = [
        migrations.AddField(
            model_name="shopitem",
            name="task_tag",
            field=models.CharField(
                choices=[("ribbon","Ribbon"),("cookie","Cookie"),("pizza","Pizza"),("general","General")],
                default="general", max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="shopitem",
            name="theme_key",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]
