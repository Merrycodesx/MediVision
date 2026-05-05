from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class EmployeeType(models.TextChoices):
        CLINICIAN = 'C', _("Clinician")
        RADIOLOGIST = 'R', _("Radiologist")
        LOCAL_ADMIN = 'L', _("Administrator_Local")
        AUDITOR = 'A', _("Auditor")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='users')
    username = models.CharField(max_length=15, null=True, unique=True)
    email = models.EmailField(_('email_address'), unique=True)
    native_name = models.CharField(max_length=20)
    phone_num = models.CharField(max_length=12)
    password = models.CharField(max_length=255, null=False)
    role = models.CharField(
        max_length=1,
        choices=EmployeeType.choices,
        default=EmployeeType.CLINICIAN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email}"


class Patient(models.Model):
    class SexChoices(models.TextChoices):
        MALE = 'M', _("Male")
        FEMALE = 'F', _("Female")

    full_name = models.CharField(max_length=35, null=False)
    age = models.IntegerField(null=False)
    sex = models.CharField(
        max_length=1,
        choices=SexChoices
    )
    hiv_Status = models.BooleanField(default=False)
    symptoms = models.TextField(default='[]')  # JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='patients')
    clinician_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.full_name}"


class Screening(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='screenings')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_screenings')
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='screenings')
    tb_score = models.FloatField(default=0.0)
    triage_recommendation = models.CharField(max_length=255, blank=True, default='')
    heatmap_url = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Screening {self.id} - {self.patient.full_name}"


class ClinicalData(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='clinical_data')
    symptoms = models.TextField()  # JSON string
    risk_factors = models.TextField()  # JSON string
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    smoker = models.BooleanField(default=False)
    hiv_positive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Clinical data for {self.patient.full_name}"


class ImageRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='images')
    image_path = models.CharField(max_length=512)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for {self.patient.full_name}"


class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    genexpert = models.CharField(max_length=120, blank=True, default='')
    smear = models.CharField(max_length=120, blank=True, default='')
    culture = models.CharField(max_length=120, blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_lab_results')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LabResult {self.id} for {self.patient.full_name}"


class Feedback(models.Model):
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='feedbacks')
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} on {self.screening.id}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=120, blank=True)
    target_id = models.CharField(max_length=128, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit {self.id}: {self.action} by {self.user.email}"

