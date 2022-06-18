# Api B2B Capel
Api for Capel enterprise

# Descripción
Este proyecto contiene varios microservicios o endpoints para recuperar datos de relevancia para Capel

### Instalación
Instalar librerías y dependencias necesarias

```
pip install -r requirements.txt
```
#### Configurar los parámetros de la conexión

##### Servidor de base de datos:
```
DB_HOST = ""
DB_PORT = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""
```
##### Servidor de autenticación
```
MONGODBUSER = ""
MONGODBPASSWD = ""
```
### EndPoints

- /api/v1/login
- /api/v1/data?initialdate=yyyymmdd&finaldate=yyyymmdd
- /api/v1/dailydata?initialdate=yyyymmdd
- /api/v1/dailydata?initialdate=yyyymmdd
- /api/v1/monthlydata?initialdate=yyyymmdd
- /api/v1/filtercadena?initialdate=yyyymmdd&finaldate=yyyymmdd&retail=$retail&comuna=$comuna&marca=$marca&ciudad=$ciudad
- /api/v1/filtercadena?initialdate=yyyymmdd&finaldate=yyyymmdd&retail=$retail
- /api/v1/filtermarca?initialdate=yyyymmdd&finaldate=yyyymmdd&marca=$marca
- /api/v1/filtermarca?initialdate=yyyymmdd&finaldate=yyyymmdd&ciudad=$ciudad
- /api/v1/filtermarca?initialdate=yyyymmdd&finaldate=yyyymmdd&comuna=$comuna
- /api/v1/populate
- /api/v1/docs

### Tecnologías
- Python 3.10
- Flask




