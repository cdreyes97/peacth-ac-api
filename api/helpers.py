import numpy as np
import pandas as pd
from rest_framework.serializers import Serializer
from api import serializers
import json
from api.models import *
from api.serializers import *

#RN
import tensorflow as tf 
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import Callback, ModelCheckpoint
from tensorflow.keras.layers import Dropout
import tensorflow as tf 
from keras import backend as k
from tensorflow.keras import layers
import keras
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Dropout, Input, concatenate, Flatten, InputLayer, LSTM
from keras.utils.vis_utils import plot_model
from keras.callbacks import ModelCheckpoint
from keras import Model
import datetime


#network_weights = []



def calculate_dosis(data,params):
    age = data['age']
    #print(age)
    men = 1 if data['sex'] == 'M' else 0
    #print(men)
    initialINR = data['initialINR']
    #print(initialINR)
    imc = data['imc']
    #print(imc)
    CYP2C9_2_12 = 1 if data['genetics']['CYP2C9_2'] == '*1/*2' else 0
    #print(CYP2C9_2_12)
    CYP2C9_3_13 = 1 if data['genetics']['CYP2C9_3'] == '*1/*3' else 0
    #print(CYP2C9_3_13)
    CYP2C9_3_33 = 1 if data['genetics']['CYP2C9_3'] == '*3/*3' else 0
    #print(CYP2C9_3_33)
    VKORC1_GA = 1 if data['genetics']['VKORC1'] == 'G/A' else 0
    #print(VKORC1_GA)
    VKORC1_AA = 1 if data['genetics']['VKORC1'] == 'A/A' else 0
    #print(VKORC1_AA)

    logWTD = params.p_0 + (params.p_men * men) + (age * params.p_age) + (initialINR * params.p_initialINR) + (imc * params.p_imc) + (CYP2C9_2_12 * params.p_CYP2C9_12) + (CYP2C9_3_13 * params.p_CYP2C9_13) + (CYP2C9_3_33 * params.p_CYP2C9_33) + (VKORC1_GA * params.p_VKORC1_GA) + (VKORC1_AA * params.p_VKORC1_AA)
    #print(logWTD)
        
    return np.exp(logWTD)


def make_data_frame(genetic, dosis):
    df_g = pd.DataFrame(genetic)
    df_d = pd.DataFrame(dosis, columns = ['dosis'])

    df_genetics = pd.concat([df_d, df_g], axis=1)

    return df_genetics

def patients_dataframe(patients, RN = False):
    genetics_values = {'CYP2C9_2' : {'*1/*1':1, '*1/*2':2, '*2/*2':3},
                       'CYP2C9_3' : {'*1/*1':1, '*1/*3':2, '*3/*3':3},
                       'VKORC1'   : {'G/G':1, 'G/A':2, 'A/A':3}}
    columns = ['sex', 'age', 'inr', 'imc', 'cyp2c92', 'cyp2c93', 'vkorc1','dose']


    columns_values = [[],[],[],[],[],[],[],[]]

    for p in patients:
        patient = {}
        genetics = {}
        if len(patients) > 1:
            serializer = PatientSerializer(p)
            patient = serializer.data
            genetics = json.loads(patient['genetics'])
        else:
            patient = p
            genetics = p['genetics']
        

        if patient['sex'] == 'M':
            columns_values[0].append(2)
        else:
            columns_values[0].append(1)
        
        columns_values[1].append(patient['age'])
        columns_values[2].append(patient['initialINR'])
        columns_values[3].append(patient['imc'])
        columns_values[7].append(patient['weeklyDoseInRange'])

        if not RN:
            columns_values[4].append(genetics_values['CYP2C9_2'][genetics['CYP2C9_2']])
            columns_values[5].append(genetics_values['CYP2C9_3'][genetics['CYP2C9_3']])
            columns_values[6].append(genetics_values['VKORC1'][genetics['VKORC1']])
        else:
            columns_values[4].append(genetics)
        
    df = pd.DataFrame(columns_values, columns).T

    if RN:
        df = df.drop(columns=['cyp2c93','vkorc1'])
        df = df.rename(columns={'cyp2c92':'genetics'})
    else:
        df['logdose'] = np.log2(df['dose'])

    return df

def switch_CYP2C9(argument):
    switcher = {
        "*1/*1-*1/*1": {'rs1799853':'Ausente'       ,'rs1057910':'Ausente'      ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador extensivo o silvestre (EM)"},
        "*1/*1-*1/*3": {'rs1799853':'Ausente'       ,'rs1057910':'Heterocigoto' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador intermedio (IM)"},
        "*1/*1-*3/*3": {'rs1799853':'Heterocigoto'  ,'rs1057910':'Ausente'      ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador extensivo o silvestre (EM)"},
        "*1/*2-*1/*1": {'rs1799853':'Heterocigoto'  ,'rs1057910':'Heterocigoto' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador intermedio (IM)"},
        "*1/*2-*1/*3": {'rs1799853':'Ausente'       ,'rs1057910':'Doble mutado' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador deficiente o pobre (PM)"},
        "*1/*2-*3/*3": {'rs1799853':'Doble mutado'  ,'rs1057910':'Ausente'      ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador extensivo o silvestre (EM)"},
        "*2/*2-*1/*1": {'rs1799853':'Doble mutado'  ,'rs1057910':'Doble mutado' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador deficiente o pobre (PM)"},
        "*2/*2-*1/*3": {'rs1799853':'Heterocigoto'  ,'rs1057910':'Doble mutado' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador deficiente o pobre (PM)"},
        "*2/*2-*3/*3": {'rs1799853':'Doble mutado'  ,'rs1057910':'Heterocigoto' ,'Observaciones':"El genotipo del paciente corresponde a un metabolizador intermedio (IM)"}
    }
    return switcher.get(argument, "Invalid combination")

def switch_VKORC1(argument):
    switcher = {
        "G/G": {'rs9923231':'Ausente (G/G)'     , 'Observaciones':"El genotipo del paciente es normal"},
        "G/A": {'rs9923231':'Heterocigoto (G/A)', 'Observaciones':"El genotipo del paciente se relaciona con una menor dosis de Acenocumarol"},
        "A/A": {'rs9923231':'Doble mutado (A/A)', 'Observaciones':"El genotipo del paciente se relaciona con una menor dosis de Acenocumarol"},
    }
    return switcher.get(argument, "Invalid combination")

def categorical_data_preprocessing(df):
  #Variables genéticas
  df['genetics'].values[0]
  genetics = pd.DataFrame(list(df['genetics'].values))
  gen_df = pd.get_dummies(genetics)

  #Sexo
  sex_df = pd.get_dummies(df['sex'], prefix='sex')

  return pd.concat([sex_df,gen_df],axis=1) 

def data_preprocessing(data, prediction=False):
  '''
  code                 BORRAR
  sex                  CATEGORICO
  initialDate          BORRAR
  initialDose          NUMERICA
  initialINR           NUMERICA
  weeklyDoseInRange    PREDECIR
  totalDays            BORRAR
  weight               BORRAR
  height               BORRAR
  imc                  NUMERICA
  age                  NUMERICA
  genetics             CATEGORICO
  '''
  categorical_df = categorical_data_preprocessing(data)

  #Crear nuevo dataframe
  new_df = pd.concat([data,categorical_df],axis=1)
  y = []
  if not prediction: 
    y = new_df['dose']
  new_df = new_df.drop(columns=['sex','genetics','dose'],axis=1)

  
  return new_df, y

def minmax_norm(df, min, max):
  return (df- min) / (max - min)

def r_minmax_norm(df, min, max):
  return df*(max - min) + min

def predict_dose(model, patient, X_min_max, y_min_max):
    
    df = patients_dataframe([patient], True)
    X, _ = data_preprocessing(df, True)

    #print(df.dtypes)
    #print(df)

    #print(X)

    X_norm = minmax_norm(X, X_min_max[0], X_min_max[1])

    #print(type(X_norm))

    X_norm = X_norm.fillna(0)
    X_norm = X_norm.astype('float64')
    

    #print(X_norm)

    networkDoseNorm = model.predict(X_norm)

    #print(networkDoseNorm)

    networkDose = r_minmax_norm(networkDoseNorm, y_min_max[0], y_min_max[1])

    #print(networkDose)

    return networkDose[0][0]

def get_date():
    mes = {'01':'enero', '02':'febrero', '03':'marzo', '04':'abril', '05': 'mayo', '06':'junio',
       '07':'julio', '08':'agosto', '09':'septiembre', '10':'octubre', '11': 'noviembre', '12':'diciembre'}
           
    x = datetime.datetime.now()

    l = x.strftime("%x").split("/")

    return "{} de {}".format(l[1], mes[l[0]])
