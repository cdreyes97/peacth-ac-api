from typing import Collection
from PeacthAC.settings import DATABASES
from rest_framework import response
from rest_framework.serializers import Serializer
from rest_framework.exceptions import AuthenticationFailed
from api import serializers
from rest_framework.decorators import api_view,schema
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import *
from api.serializers import *
import numpy as np
import pandas as pd
import statsmodels.api as sfm
from rest_framework.views import APIView
import datetime
import json
from rest_framework import serializers as rest_serializers
from api.helpers import * 
import pymongo
from pymongo import MongoClient
from bson.binary import Binary
import pickle
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives, message
from django.conf import settings 
from email.mime.image import MIMEImage
import os
import jwt

client = MongoClient('mongodb+srv://kinewen:QMDIoiQ5BwS8GY5V@kinewen-cluster.skote.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client['peacth-ac']


#y_min_max = []
#X_min_max = []



# Create your views here.
class PatientModelViewSet(viewsets.ModelViewSet):
    
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()

    def retrieve(self, request, pk=None):
        try:
            object = Patient.objects.get(code=pk)

            serializer = self.get_serializer(object)

            data = serializer.data
            data['genetics'] = json.loads(data['genetics'])

            return Response(data, status=status.HTTP_200_OK)
        except:            
            return Response({"message" : "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        try:
            patientsObjects = Patient.objects.all()
            serializer = self.get_serializer(patientsObjects, many=True)

            patients = serializer.data

            for p in patients:
                p['genetics'] = json.loads(p['genetics'])

            return Response(patients, status=status.HTTP_200_OK)
        except:
            return Response({"message" : "NULL"}, status=status.HTTP_404_NOT_FOUND)

        
    @action(detail=False, methods=['post'])
    def get_weekly_dosis(self, request, pk=None):

        self.serializer_class = PatientSerializer

        request_data = request.data

        #print(request_data['code'])

        serializer = PatientSerializer(data=request_data)
        #print(X_min_max)
        #print(serializer.is_valid())

        if serializer.is_valid():

            #print(network_weights)
            
            #serializer.save()

            #patient = Patient.objects.get(code=request_data['code'])
            #print(request_data)

            param = LogWTDparameters.objects.last()

            network_model = db['api_network_models'].find_one({}, sort=[( '_id', pymongo.DESCENDING )])

            network_weights = pickle.loads(network_model['weights'])
            y_min_max = pickle.loads(network_model['y_min_max'])
            X_min_max = pickle.loads(network_model['X_min_max'])

            model = tf.keras.Sequential()
            model.add(layers.Input(shape=(13,)))
            model.add(layers.Dense(128, activation="tanh", name='hidden'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(64, activation="tanh", name='hidden2'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(32, activation="tanh", name='hidden3'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(1, activation="sigmoid", name='output'))

            model.compile(loss=tf.keras.losses.mean_absolute_error, optimizer='Adam', metrics=['accuracy'])

            model.set_weights(network_weights)

            networkDose = predict_dose(model, request_data, X_min_max, y_min_max)

            print(networkDose)

            regressionDose = calculate_dosis(request_data, param)
            
            

            
            '''
            if serializer.is_valid():
                
                initial_control = {
                    'patientCode' : request_data['code'],
                    'controlDate' : request_data['initialDate'],
                    'arrivalDose' : 0,
                    'updatedDose': initialDose,
                    'arrivalINR': request_data['initialINR'],
                    'inrInRange': False
                }

                control_serializer = ClinicalControlSerializer(data=initial_control)
                if control_serializer.is_valid():
                    control_serializer.save()
                    serializer.save()
                    response = {
                        'initialDose' : initialDose
                    }
                '''

            response = {
                    'regressionDose' : regressionDose,
                    'networkDose' : networkDose
                }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_dose(self, request, pk=None):

        patient = request.data

        serializer = PatientSerializer(data=patient)

        if serializer.is_valid():
            

            initial_control = {
                    'patientCode' : patient['code'],
                    'controlDate' : patient['initialDate'],
                    'arrivalDose' : 0,
                    'updatedDose': patient['initialDose'],
                    'arrivalINR': patient['initialINR'],
                    'inrInRange': False
                }

            control_serializer = ClinicalControlSerializer(data=initial_control)
            if control_serializer.is_valid():
                control_serializer.save()
                serializer.save()
                response = {
                    'message' : 'Dosis fijada correctamente',
                    'initialDose' : patient['initialDose']
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(control_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def calculate_all_patients(self, request):
        patients = Patient.objects.filter(weeklyDoseInRange__gt=0)
        serializer = serializer = self.get_serializer(patients, many=True)

        patients_json = serializer.data
        #print(patients_json)
        for p in patients_json:
            p['genetics'] = json.loads(p['genetics'])
            param = LogWTDparameters.objects.last()

            network_model = db['api_network_models'].find_one({}, sort=[( '_id', pymongo.DESCENDING )])

            network_weights = pickle.loads(network_model['weights'])
            y_min_max = pickle.loads(network_model['y_min_max'])
            X_min_max = pickle.loads(network_model['X_min_max'])

            model = tf.keras.Sequential()
            model.add(layers.Input(shape=(13,)))
            model.add(layers.Dense(128, activation="tanh", name='hidden'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(64, activation="tanh", name='hidden2'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(32, activation="tanh", name='hidden3'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(1, activation="sigmoid", name='output'))

            model.compile(loss=tf.keras.losses.mean_absolute_error, optimizer='Adam', metrics=['accuracy'])

            model.set_weights(network_weights)

            networkDose = predict_dose(model, p, X_min_max, y_min_max)

            regressionDose = calculate_dosis(p, param)

            result = {
                    'code' : p['code'],
                    'network_result' : regressionDose,
                    'regression_result' : networkDose,
                    'network_error' : abs(networkDose-p['weeklyDoseInRange'])/p['weeklyDoseInRange'],
                    'regression_error': abs(regressionDose-p['weeklyDoseInRange'])/p['weeklyDoseInRange'],
                    'final_dose' : p['weeklyDoseInRange'],
                    'is_treatement_done' : True
                }
            
            result_serializer = ModelsResultsSerializer(data=result)

            if result_serializer.is_valid():
                result_serializer.save()
            

            
        
        return Response({'message' : 'All patients calculated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def genetic_analysis(self, request, pk=None):
        
        patient = Patient.objects.get(code=pk)

        genetics = patient.genetics

        cyp2c9_comb = genetics['CYP2C9_2'] + "-" + genetics['CYP2C9_3']
        vkorc1 = genetics['VKORC1']

        cyp2c9_analysis = switch_CYP2C9(cyp2c9_comb)
        vkorc1_analysis = switch_VKORC1(vkorc1)

        response = {
            "CYP2C9": cyp2c9_analysis,
            "VKORC1" : vkorc1_analysis
        }

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def patient_profile(self, request, pk=None):
        try:
            object = Patient.objects.get(code=pk)

            serializer = self.get_serializer(object)

            response = {}
            
            # Clinic information
            patient = serializer.data
            genetics = object.genetics
            patient['genetics'] = json.loads(patient['genetics'])

            response['clinic'] = patient

            # Genetic profile
            cyp2c9_comb = genetics['CYP2C9_2'] + "-" + genetics['CYP2C9_3']
            vkorc1 = genetics['VKORC1']

            cyp2c9_analysis = switch_CYP2C9(cyp2c9_comb)
            vkorc1_analysis = switch_VKORC1(vkorc1)

            gen_analysis = {
                "CYP2C9": cyp2c9_analysis,
                "VKORC1" : vkorc1_analysis
            }

            response['genetic'] = gen_analysis

            # Treatement progress
            visits = ClinicalControl.objects.filter(patientCode=pk)

            first = True
            
            dates = []
            inrValues = []
            doseValues = []

            for v in visits:
                '''
                if first:
                    dates.append(v.controlDate.strftime("%d/%m/%Y"))
                    inrValues.append(v.arrivalINR)
                    doseValues.append(0)
                    first = False
                else:
                    dates.append(v.controlDate.strftime("%d/%m/%Y"))
                    inrValues.append(v.arrivalINR)
                    doseValues.append(v.arrivalDose)
                '''
                dates.append(v.controlDate.strftime("%d/%m/%Y"))
                inrValues.append(v.arrivalINR)
                doseValues.append(v.updatedDose)
            historicINR = {
                "dates" : dates,
                "inrValues" : inrValues,
                "doseValues" : doseValues
            }

            response["historicINR"] = historicINR

            return Response(response, status=status.HTTP_200_OK)
        except:            
            return Response({"message" : "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ClinicalControlViewSet(viewsets.ModelViewSet):   

    serializer_class = ClinicalControlSerializer
    queryset = ClinicalControl.objects.all()

    @action(detail=False, methods=['post'])
    def register_visit(self, request, pk=None):

        self.serializer_class = ClinicalControlSerializer

        request_data = request.data

        serializer = ClinicalControlSerializer(data=request_data)
        patient = Patient.objects.get(code=request_data['patientCode'])
        #print(patient.code)
        

        if serializer.is_valid():
            initialDate = patient.initialDate
            newDate = request_data['controlDate'].split('-')
            controlDate = datetime.date(int(newDate[0]),int(newDate[1]),int(newDate[2]))
            delta = controlDate - initialDate
            patient.totalDays = delta.days
            #print(delta.days)
            #print(patient.totalDays)
            if request_data['inrInRange']:
                patient.weeklyDoseInRange = request_data['arrivalDose']
            patient.save()
            serializer.save()
            response = {
                'message' : 'Saved Succesfully'
            }
            return Response(response, status=status.HTTP_200_OK)
        

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def get_last(self, request, pk=None):

        last = ClinicalControl.objects.filter(patientCode=pk).order_by('-_id')[0]

        serializer = self.serializer_class(last)

        return Response(serializer.data, status=status.HTTP_200_OK)

class LogWTDparametersViewSet(viewsets.ModelViewSet):

    serializer_class = LogWTDparametersSerializer
    queryset = LogWTDparameters.objects.all()

    @action(detail=True, methods=['post'])
    def set_parametres(self, request, pk=None):
        self.serializer_class = LogWTDparametersSerializer

        request_data = request.data

        serializer = LogWTDparametersSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            response = {
                'message' : 'Parámetros actualizados correctamente'
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def get_last(self, request, pk=None):
        self.serializer_class = LogWTDparametersSerializer

        last_parameters = LogWTDparameters.objects.last()
        json = LogWTDparametersSerializer(last_parameters)
        #print(json.data)


        return Response(json.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def multivariable_regression(self, request):
        patients = Patient.objects.filter(weeklyDoseInRange__gt=0)

        df = patients_dataframe(patients)
        #print(df.head())

        lm = sfm.OLS.from_formula(formula="logdose~C(sex)+age+inr+imc+C(cyp2c92)+C(cyp2c93)+C(vkorc1)", data=df).fit()

        #print(lm.summary())
        #print(lm.params)
        params = lm.params
        parameters = {
                    "p_0": params[0],
                    "p_men": params[1],
                    "p_age": params[7],
                    "p_initialINR": params[8],
                    "p_imc": params[9],
                    "p_CYP2C9_12": params[2],
                    "p_CYP2C9_13": params[3],
                    "p_CYP2C9_33": params[4],
                    "p_VKORC1_GA": params[5],
                    "p_VKORC1_AA": params[6],
                    "r_squared" : lm.rsquared
                }

        last_parameters = LogWTDparameters.objects.last()

        if last_parameters.r_squared < lm.rsquared:
            self.serializer_class = LogWTDparametersSerializer
            serializer = LogWTDparametersSerializer(data=parameters)

            if serializer.is_valid():
                serializer.save()
                response = {
                    'message' : 'Parámetros actualizados correctamente'
                }
                response['params'] = parameters
                return Response(response, status=status.HTTP_200_OK)
            return Response({'message' : 'Problem updating parameters'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        response = {'message' : 'Los parámetros no se actualizaron debido a que el r2 es menor a la regresión actual'}
        response['params'] = LogWTDparametersSerializer(last_parameters).data

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def neural_network(self, request):

        '''
        {   
            "_id": ObjectID,
            "weights" : binary,
            "y_min_max": list,
            "X_min_max": list,
            "numberOfPatients": int,
            "created_at": date,
        }
        '''

        last = {}
        network_collection = db['api_network_models']
        if (not (network_collection.count() == 0 or 'network_models' in db.list_collection_names())):
            last = network_collection.find_one({}, sort=[( '_id', pymongo.DESCENDING )])
        

        patients = Patient.objects.filter(weeklyDoseInRange__gt=0)

        response = {
            "is_updated" : False
        }

        if last:
            if last['numberOfPatients'] == len(patients):
                response["message"] = "No hay cambios en la cantidad de pacientes."
                return Response(response,status=status.HTTP_200_OK)
            if len(patients) - last['numberOfPatients'] < 50:
                response["message"] = "No hay pacientes nuevos suficientes."
                return Response(response,status=status.HTTP_200_OK)
  
            

        data = patients_dataframe(patients, True)

        X, y  = data_preprocessing(data)

        #normalizar
        X_min = X.min()
        X_max = X.max()
        y_min = y.min()
        y_max = y.max()

        #global y_min_max
        #global X_min_max

        y_min_max = [y_min, y_max]
        X_min_max = [X_min, X_max]

        #print(X_min_max)

        y_norm = minmax_norm(y, y_min, y_max)
        X_norm = minmax_norm(X, X_min, X_max)

        X_train, X_test, y_train, y_test = train_test_split(X_norm, y_norm, test_size = 0.3, random_state=0)

        X_train = X_train.astype('float64')
        y_train = y_train.astype('float64')
        X_test  = X_test.astype('float64')
        y_test  = y_test.astype('float64')

        model = tf.keras.Sequential()
        model.add(layers.Input(shape=(13,)))
        model.add(layers.Dense(128, activation="tanh", name='hidden'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(64, activation="tanh", name='hidden2'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(32, activation="tanh", name='hidden3'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(1, activation="sigmoid", name='output'))

        model.compile(loss=tf.keras.losses.mean_absolute_error, optimizer='Adam', metrics=['accuracy'])
        #print(model.summary())

        cb = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=25)

        history = model.fit(X_train, 
                            y_train,
                            validation_data=(X_test, y_test),
                            batch_size=32,
                            epochs=100, 
                            verbose=1,
                            callbacks=[cb])

        #a = X_norm.astype('float64').head(5)

        #w = model.predict(a)

        network_weights = model.get_weights()
        #print(history.history['val_accuracy'][-1])

        weights_bin = Binary(pickle.dumps(network_weights, protocol=2), subtype=128 )
        y_min_max_bin = Binary(pickle.dumps(y_min_max, protocol=2), subtype=128 )
        X_min_max_bin = Binary(pickle.dumps(X_min_max, protocol=2), subtype=128 )


        date = datetime.datetime.now()
        dt_string = date.strftime("%d/%m/%Y %H:%M:%S")

        doc = {
                "loss": history.history['val_loss'][-1],   
                "weights" : weights_bin,
                "y_min_max": y_min_max_bin,
                "X_min_max": X_min_max_bin,
                "numberOfPatients": len(patients),
                "created_at": date
            }
        
        network_id = network_collection.insert_one(doc).inserted_id

        #print("Document with " + str(network_id) + " saved successfully.")

        #arrx = pickle.loads(binary)

        #for i in range(len(network_weights)):        
        #    print(np.array_equal(network_weights[i], arrx[i]))



        #print(r_minmax_norm(w, y_min, y_max))

        response = {
            "is_updated" : True,
            "message" : "Red neuronal actualizada.",
            "loss" : history.history['loss'][-1],
            "updated_at" : dt_string
        }

        return Response(response,status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_last_neural_network(self, request):

        last_nn = db['api_network_models'].find_one({}, sort=[( '_id', pymongo.DESCENDING )])

        response = {
            "loss" : "-",
            "created_at" : "-"
        }

        if last_nn != None:
            response = {
                "loss" : str(round(last_nn["loss"]*100,2)) + "%",
                "created_at" : last_nn["created_at"].strftime("%d/%m/%Y %H:%M:%S")
            }
            
            return Response(response,status=status.HTTP_200_OK)
        
        return Response(response,status=status.HTTP_200_OK)

class ModelsResultsModelViewSet(viewsets.ModelViewSet):
    serializer_class = ModelsResultsSerializer
    queryset = ModelsResults.objects.all()

class BoxplotVizualitation(APIView):

    #@api_view(['GET'])
    #@schema(None)
    def get(self,request,format=None,**kwargs):
        
        #Petición
        x = kwargs['variable']
        

        genetic = [patient.genetics for patient in Patient.objects.filter(weeklyDoseInRange__gt=0)]
        dosis = [patient.weeklyDoseInRange for patient in Patient.objects.filter(weeklyDoseInRange__gt=0)]

        gens = make_data_frame(genetic, dosis)

        y = gens[x].unique()

        #print(y)

        l= []

        for i in y:
            aux = {}

            fillter= gens[x] == i
            gens_f = gens[fillter]

            #[min, Q1, Q2, Q3, max]
            q1 = np.percentile(gens_f['dosis'],25)
            q2 = np.percentile(gens_f['dosis'],50)
            q3 = np.percentile(gens_f['dosis'],75)
            mn = q1 - 1.5*(q3-q1)
            mx = q3 + 1.5*(q3-q1)

            aux['label'] = i
            aux['value'] = [mn, q1, q2 ,q3, mx]

            l.append(aux)

            #print(mn,q1,q2,q3,mx)

        response = l

        return Response(response, status=status.HTTP_200_OK)

class FrequencyVizualitation(APIView):
    
    def get(self,request, **kwargs):

        #print(kwargs['variable'])

        #Petición
        x = kwargs['variable'] # 'CYP2C9_3'

        genetic = [patient.genetics for patient in Patient.objects.all()]
        dosis = [patient.weeklyDoseInRange for patient in Patient.objects.all()]

        gens = make_data_frame(genetic, dosis)

        freq = gens[x].value_counts()

        #print(freq)

        response = {
                        'labels' : freq.index.tolist(),
                        'frequency': freq
                }

        return Response(response, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_email(request):

    emailDestino = request.data['email']
    patientName = request.data['patient']
    medicName = request.data['name']
    date = get_date()
    totalDosis = request.data['totalDosis']

    context = {'patientName': patientName, 'medicName' : medicName, 'date': date, 'totalDosis': totalDosis}
    template = get_template('email.html')
    content = template.render(context)

    msg = EmailMultiAlternatives(
        'Peacth-AC',
        'Kiñewen',
        settings.EMAIL_HOST_USER,
        [emailDestino]
    )

    msg.attach_alternative(content,'text/html')

    images = ['logo-color.png', 'facebook.png','instagram.png']

    for i,img in enumerate(images,start=1):
        fp = open('templates/img/'+img, 'rb')
        image = MIMEImage(fp.read())
        fp.close()
        image.add_header('Content-ID', '<img'+str(i)+'>')
        msg.attach(image)

    msg.send()

    response = {
                'response' : 'correo enviado con exito'
                }
        
    return Response(response, status=status.HTTP_200_OK)

class MedicalStaffModelViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalStaffSerializer
    queryset = MedicalStaff.objects.all()       

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data['email']
        password = request.data['password']

        staff = MedicalStaff.objects.filter(email=email).first()

        if staff is None:
            raise AuthenticationFailed("User not Found")

        if password != staff.password:
            raise AuthenticationFailed("Incorrect Password")
        

        payload = {
            "rut" : staff.rut,
            "name" : staff.name,
            "last_name" : staff.last_name,
            "type" : "medical_staff"
        }

        token = jwt.encode(payload, "secret", algorithm='HS256').decode('utf-8')

        response = Response()
        
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response

    @action(detail=False, methods=['post'])
    def logout(self, request):

        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message' : 'Logout success'
        }

        return response

    @action(detail=False, methods=['post'])
    def get_session(self, request, pk=None):
        token = request.data['jwt']

        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        payload = jwt.decode(token, 'secret', algorithm=['HS26'])
        

        med = MedicalStaff.objects.filter(rut=payload['rut']).first()
        serializer = self.serializer_class(med)

        return Response(serializer.data)

class LaboratoryWorkerModelViewSet(viewsets.ModelViewSet):
    serializer_class = LaboratoryWorkerSerializer
    queryset = LaboratoryWorker.objects.all()       

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data['email']
        password = request.data['password']

        staff = LaboratoryWorker.objects.filter(email=email).first()

        if staff is None:
            raise AuthenticationFailed("User not Found")

        if password != staff.password:
            raise AuthenticationFailed("Incorrect Password")
        

        payload = {
            "email" : staff.email,
            "name" : staff.name,
            "last_name" : staff.last_name,
            "type" : "laboratory_worker"
        }

        token = jwt.encode(payload, "secret", algorithm='HS256').decode('utf-8')

        response = Response()
        
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response

    @action(detail=False, methods=['post'])
    def logout(self, request):

        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message' : 'Logout success'
        }

        return response

    @action(detail=False, methods=['post'])
    def get_session(self, request, pk=None):
        token = request.data['jwt']

        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        payload = jwt.decode(token, 'secret', algorithm=['HS26'])
        

        med = LaboratoryWorker.objects.filter(email=payload['email']).first()
        serializer = self.serializer_class(med)

        return Response(serializer.data)