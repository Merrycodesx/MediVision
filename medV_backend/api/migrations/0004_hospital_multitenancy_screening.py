# Generated manually for multi-hospital tenancy and patient-linked inference

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_remove_patient_cxr_image_alter_user_role_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Hospital",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="hospital",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="users", to="api.hospital"),
        ),
        migrations.AddField(
            model_name="patient",
            name="hospital",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="patients", to="api.hospital"),
        ),
        migrations.CreateModel(
            name="Screening",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tb_score", models.FloatField(default=0.0)),
                ("triage_recommendation", models.CharField(blank=True, default="", max_length=255)),
                ("heatmap_url", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "hospital",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="screenings", to="api.hospital"),
                ),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="screenings", to="api.patient"),
                ),
                (
                    "requested_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="requested_screenings", to="api.user"),
                ),
            ],
        ),
    ]
