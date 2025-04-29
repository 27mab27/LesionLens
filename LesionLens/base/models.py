from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('specialist', 'Specialist'), 
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)  
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)  

    def __str__(self):
        return self.get_full_name() or self.username


class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True, blank=False, null=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    weight = models.FloatField()
    height = models.FloatField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.full_name


class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'specialist'}
    )
    image = models.ImageField(upload_to='diagnosis_images/')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Lesion', 'Lesion'), ('Non-Lesion', 'Non-Lesion'), ('Pending', 'Pending')],
        default='Pending'
    )
    report_pdf = models.FileField(upload_to='diagnosis_reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.status}"
