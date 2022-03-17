from datetime import datetime
from djongo import models
import datetime

isMigrate = True

# Create your models here.
class Genetic(models.Model):
    CYP2C9_2 = models.CharField(unique=True, max_length=5)
    CYP2C9_3 = models.CharField(unique=True, max_length=5)
    VKORC1 = models.CharField(unique=True, max_length=5)

    class Meta:
        abstract = isMigrate


class Patient(models.Model):
    _id = models.ObjectIdField()
    code = models.CharField(unique=True, max_length=5)
    sex = models.CharField(max_length=1)
    initialDate = models.DateField(default=datetime.date.today)
    initialDose = models.FloatField(default=0)
    initialINR = models.FloatField()
    weeklyDoseInRange = models.FloatField(default=0)
    totalDays = models.IntegerField(default=0)
    weight = models.FloatField()
    height = models.FloatField()
    imc = models.FloatField()
    age = models.IntegerField(default=0)

    genetics = models.EmbeddedField(
        model_container=Genetic
    )

    objects = models.DjongoManager()

class ClinicalControl(models.Model):
    _id = models.ObjectIdField()
    patientCode = models.CharField(max_length=5)
    controlDate = models.DateField(default=datetime.date.today)
    arrivalDose = models.FloatField(default=0)
    updatedDose = models.FloatField(default=0)
    arrivalINR = models.FloatField(default=0)
    inrInRange = models.BooleanField(default=False)

class LogWTDparameters(models.Model):
    _id = models.ObjectIdField()
    p_0 = models.FloatField(default=0)
    p_men = models.FloatField(default=0)
    p_age = models.FloatField(default=0)
    p_initialINR  = models.FloatField(default=0)
    p_imc = models.FloatField(default=0)
    p_CYP2C9_12  = models.FloatField(default=0)
    p_CYP2C9_13 = models.FloatField(default=0)
    p_CYP2C9_33 = models.FloatField(default=0)
    p_VKORC1_GA = models.FloatField(default=0)
    p_VKORC1_AA = models.FloatField(default=0)
    r_squared = models.FloatField(default=0)

class ModelsResults(models.Model):
    _id = models.ObjectIdField()
    code = models.CharField(unique=True, max_length=5)
    network_result = models.FloatField(default=0)
    regression_result = models.FloatField(default=0)
    network_error = models.FloatField(default=0)
    regression_error = models.FloatField(default=0)
    final_dose = models.FloatField(default=0)
    is_treatement_done = models.BooleanField(default=False)

class MedicalStaff(models.Model):
    _id = models.ObjectIdField()
    email = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    registry_number = models.CharField(unique=True, max_length=100)
    rut = models.CharField(unique=True, max_length=100)

class LaboratoryWorker(models.Model):
    _id = models.ObjectIdField()
    email = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)