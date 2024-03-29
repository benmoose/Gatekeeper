# Generated by Django 2.2.1 on 2019-05-11 14:46

from django.db import migrations, models

import db.user.models.user


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("created_on", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_on", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "user_id",
                    models.CharField(
                        default=db.user.models.user.generate_user_id,
                        max_length=128,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("phone_number", models.CharField(max_length=32, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"abstract": False},
        )
    ]
