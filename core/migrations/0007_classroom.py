from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_userprofile_role"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Classroom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=80)),
                ("join_code", models.CharField(max_length=20, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("teacher", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="classrooms",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.AddField(
            model_name="userprofile",
            name="classroom",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="core.classroom",
            ),
        ),
    ]
