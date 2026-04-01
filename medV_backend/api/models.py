from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.postgres.fields import ArrayField
# Create your models here.


<<<<<<< HEAD
class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


=======
>>>>>>> bf1dbb5 (some update)
class User(AbstractUser):
    class EmployeeType(models.TextChoices):
        CLINICIAN = 'C', _("Clinician")
        RADIOLOGIST = 'R', _("Radiologist")
        LOCAL_ADMIN = 'L', _("Administrator_Local")
        AUDITOR = 'A', _("Auditor")
<<<<<<< HEAD


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='users')
=======
        PATIENT = 'P', _("Patient")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
>>>>>>> bf1dbb5 (some update)
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
<<<<<<< HEAD
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name='patients')
=======
>>>>>>> bf1dbb5 (some update)
    clinician_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.full_name}"


<<<<<<< HEAD
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


=======
>>>>>>> bf1dbb5 (some update)
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
    

