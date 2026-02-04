from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class User(AbstractUser):
    class EmployeeType(models.TextChoices):
        CLINICIAN = 'C', _("Clinician")
        RADIOLOGIST = 'R', _("Radiologist")
        LOCAL_ADMIN = 'L', _("Administrator_Local")
        AUDITOR = 'A', _("Auditor")
        PATIENT = 'P', _("Patient")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=15, null=True, unique=True)
    email = models.EmailField(_('email_address'), unique=True)
    native_name = models.CharField(max_length=20)
    phone_num = models.CharField(max_length=12)
    password = models.CharField(max_length=255, null=False)
    role = models.CharField(
        max_length=1,
        choices=EmployeeType.choices,
        default=EmployeeType.PATIENT
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
    symptoms = ArrayField(
        models.CharField(max_length=40)
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    clinician_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.full_name}"
    

