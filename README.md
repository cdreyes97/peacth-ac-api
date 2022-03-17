* [Inicio](#inicio)
* [Documentación API](#api)
* [Ayudas](#ayudas)

* [Tecnologias](#tec)

<div id='inicio' />

# Run Peacth-AC API

Instalar requerimientos
```
pip install -r requeriments.txt
```

Se requiere tener una base de datos en mongoDB
```
use peacth-ac
```

Borrar "0001_initial.py"

```
python3 manage.py makemigrations api
python3 manage.py migrate

```

<div id='api' />

# Documentación API

### API root
- https://peacth-ac-backend.herokuapp.com/api/
### ESTIMACIÓN DE DOSIS
#### Calcular dosis semanal [POST]
This method calculate the dose of the patients
- https://peacth-ac-backend.herokuapp.com/api/patients/get_weekly_dosis/get_weekly_dosis/
+ Request (application/JSON)
	+ Body
    ```
    {
    		"code": "T-001",             
    		"sex": "M",                  
    		"initialDate": "2009-11-30", 
    		"initialDose": 6.0,          
    		"initialINR": 1.1,           
    		"weeklyDoseInRange": 10.0,   
    		"totalDays": 534, 	     
    		"weight": 80.0, 	     
    		"height": 1.68, 	     
    		"imc": 28.3,                
    		"age": 69,                   
    		"genetics": {
				"CYP2C9_2": "*1/*1", 
    			"CYP2C9_3": "*1/*1", 
    			"VKORC1": "A/A"      
    		}
    }
	```
+ Response (application/JSON)
	```
	{
	"initialDose": 8.543749816393767 
	}
	```
### Registra visitas
#### Ver todos los controles registrados [GET]
This method allows us to see all the information about medical checks.
- https://peacth-ac-backend.herokuapp.com/api/clinical_control/
+ Response (application JSON)
	```
	{ 
		"_id":  "60f1e93f08956a1ceb4ffb5a",  
		"patientCode":  "T-999",  
		"controlDate":  "2009-11-30",  
		"arrivalDose":  0.0,  
		"updatedDose":  9.929399471052776,  
		"arrivalINR":  1.1,  
		"inrInRange":  false
	}
	```
#### Registrar visita [POST]
This method save the information about patient's medical checks 
- https://peacth-ac-backend.herokuapp.com/api/clinical_control/register_visit/register_visit/
+ Request (application/JSON)
	+ Body
		```
		  {   
			  "patientCode":  "T-999",  
			  "controlDate":  "2009-11-30",  
			  "arrivalDose":  0.0,  
			  "updatedDose":  9.929399471052776,  
			  "arrivalINR":  1.1,  
			  "inrInRange":  false  
			}
		```
+ Response (application/JSON)
	```
	{ 
		"message": "Saved Succesfully"
	}
	```
### Actualizar parámetros del algoritmo manualmente
#### Actualizar parámetros de forma manual [POST]
This method allow us change the current parameters of the pharmacogenetics algorithm
- https://peacth-ac-backend.herokuapp.com/api/LogWTDparameters/set_parametres/set_parametres/
+ Request (application/JSON)
	+ Body
		```
		{  
			"p_0":  3.081,  
			"p_men":  0.167,  
			"p_age":  0.0081,  
			"p_initialINR":  0.055,  
			"p_imc":  0.013, 
			"p_CYP2C9_12":  0.107,  
			"p_CYP2C9_13":  0.323,  
			"p_CYP2C9_33":  0.746,  
			"p_VKORC1_GA":  0.27,  
			"p_VKORC1_AA":  0.701  
		}
		```
+ Response (application/JSON)
	```
	{ 
		"message": "Parametres updated Succesfully"
	}
	```
#### Obtener la última actualización de los parámetros [GET]
This method allow us change the current parameters of the pharmacogenetics algorithm
- https://peacth-ac-backend.herokuapp.com/api/LogWTDparameters/get_last/get_last
+ Response (application/JSON)
	```
	{
		"_id": "60f1ee881f69782bda74a492",
		"p_0": 3.081,
		"p_men": 0.167,
		"p_age": 0.0081,
		"p_initialINR": 0.055,
		"p_imc": 0.013,
		"p_CYP2C9_12": 0.107,
		"p_CYP2C9_13": 0.323,
		"p_CYP2C9_33": 0.746,
		"p_VKORC1_GA": 0.27,
		"p_VKORC1_AA": 0.701
	}
	```
### Análisis comparativo de la dosis calculada entre genotipos ingresados
+ Parameters
		+ gen (string) : the gene for which information is required
#### Información boxplot [GET]
This method get information needed to plot boxplot
- https://peacth-ac-backend.herokuapp.com/api/distributions/boxplot/{gen}
+ Response (application/JSON)
	```
	[
		{
			"label": "A/A",
			"value": [
				-0.75,
				6.0,
				8.0,
				10.5,
				17.25
			]
		},
		{
			"label": "G/A",
			"value": [
				0.5,
				11.0,
				13.25,
				18.0,
				28.5
			]
		},
		{
			"label": "G/G",
			"value": [
				2.0,
				14.0,
				18.0,
				22.0,
				34.0
			]
		}
	]
	```
#### Información distribución [GET]
This methos get information for distribution plots
- https://peacth-ac-backend.herokuapp.com/api/distributions/frequency/{gen}
+ Response (application/JSON)
	```
	{
		"labels": [
			"G/A",
			"G/G",
			"A/A"
		],
		"frequency": [
			154,
			84,
			65
		]
	}
	```

<div id='ayudas' />

# Ayudas

- [Documentación de API REST](https://www.django-rest-framework.org/).

- [Conector a base de datos](https://www.djongomapper.com/)

- [Tutorial para conexión a base de datos](https://www.mongodb.com/compatibility/mongodb-and-django)

<div id='peacth' />

# Tecnologías

- Django, MongoDB
- Heroku, MongoDB Atlas Database
- React, PrimeReact, Apexcharts
