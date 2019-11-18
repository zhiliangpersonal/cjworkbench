# Generated by Django 2.2.6 on 2019-11-08 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cjworkbench", "0002_userprofile_max_fetches_per_day")]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="locale_id",
            field=models.CharField(
                choices=[("en", "en"), ("el", "el")], default="en", max_length=5
            ),
        )
    ]
