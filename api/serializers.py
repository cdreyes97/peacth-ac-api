from rest_framework import serializers
from api.models import *


class GeneticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genetic
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class ClinicalControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalControl
        fields = '__all__'

class LogWTDparametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogWTDparameters
        fields = '__all__'

class ModelsResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelsResults
        #fields = '__all__'
        exclude = ['_id']

class MedicalStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalStaff
        fields = '__all__'
        extra_kwargs = {'password' : {'write_only': True}}

class LaboratoryWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryWorker
        fields = '__all__'
        