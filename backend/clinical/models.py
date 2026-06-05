import uuid

from django.db import models
from django.utils import timezone


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_identifier = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.patient_identifier


class Consultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="consultations")
    file_name = models.CharField(max_length=160, unique=True)
    transcript = models.TextField(blank=True)
    consultation_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-consultation_date", "-created_at"]

    def __str__(self):
        return self.file_name


class FamilyHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="family_history")
    father = models.CharField(max_length=255, blank=True)
    mother = models.CharField(max_length=255, blank=True)
    siblings = models.CharField(max_length=255, blank=True)
    others = models.CharField(max_length=255, blank=True)


class AllergicHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="allergic_history")
    food = models.CharField(max_length=255, blank=True)
    medicine = models.CharField(max_length=255, blank=True)
    pollen = models.CharField(max_length=255, blank=True)
    dust = models.CharField(max_length=255, blank=True)
    mites = models.CharField(max_length=255, blank=True)
    others = models.CharField(max_length=255, blank=True)


class PersonalHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="personal_history")
    smoking = models.CharField(max_length=255, blank=True)
    alcohol = models.CharField(max_length=255, blank=True)
    activity_level = models.CharField(max_length=255, blank=True)
    food_preferences = models.CharField(max_length=255, blank=True)
    others = models.CharField(max_length=255, blank=True)


class GynaeObsHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="gynae_obs_history")
    lmp = models.DateField(null=True, blank=True)
    edd = models.DateField(null=True, blank=True)
    para = models.CharField(max_length=255, blank=True)
    gravida = models.CharField(max_length=255, blank=True)
    alc = models.CharField(max_length=255, blank=True)
    delivery_history = models.CharField(max_length=255, blank=True)
    contraceptives_history = models.CharField(max_length=255, blank=True)
    pv_examination = models.CharField(max_length=255, blank=True)


class ChiefComplaint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="chief_complaints")
    complaint = models.CharField(max_length=255, blank=True)
    duration = models.CharField(max_length=120, blank=True)


class HealthScreening(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="health_screening")
    blood_pressure = models.CharField(max_length=120, blank=True)
    pulse_rate = models.CharField(max_length=120, blank=True)
    temperature = models.CharField(max_length=120, blank=True)
    respiratory_rate = models.CharField(max_length=120, blank=True)
    weight = models.CharField(max_length=120, blank=True)
    height = models.CharField(max_length=120, blank=True)
    bmi = models.CharField(max_length=120, blank=True)


class ClinicalExam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="clinical_exam")
    anaemia = models.CharField(max_length=255, blank=True)
    jaundice = models.CharField(max_length=255, blank=True)
    cyanosis = models.CharField(max_length=255, blank=True)
    edema = models.CharField(max_length=255, blank=True)
    systemic_examination_notes = models.TextField(blank=True)


class Investigation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="investigations")
    investigation_name = models.CharField(max_length=255, blank=True)


class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="diagnoses")
    diagnosis_name = models.CharField(max_length=255, blank=True)
    diagnosis_note = models.CharField(max_length=255, blank=True)


class Medication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="medications")
    medicine_name = models.CharField(max_length=255, blank=True)
    dosage = models.CharField(max_length=120, blank=True)
    frequency = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=120, blank=True)
    instruction = models.CharField(max_length=255, blank=True)


class Advice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="advice")
    advice_notes = models.TextField(blank=True)
