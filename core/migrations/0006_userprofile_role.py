from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0005_shopitem_task_tag")]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[("student", "Student"), ("teacher", "Teacher")],
                default="student", max_length=10,
            ),
        ),
    ]
