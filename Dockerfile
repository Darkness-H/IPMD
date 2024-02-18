# Partimos de una base oficial de python
FROM python:2.7-slim

# El directorio de trabajo es desde donde se ejecuta el contenedor al iniciarse
WORKDIR /app

# Copiamos todos los archivos del build context al directorio /app del contenedor
COPY . /app

# Ejecutamos pip para instalar las dependencias en el contenedor
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Indicamos que este contenedor se comunica por el puerto 80/tcp
EXPOSE 696

# Declaramos variables de entorno
ENV NAME World
ENV AEMET_API_KEY "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDMxNDM5NjA1QHFxLmNvbSIsImp0aSI6IjUyY2E5N2RhLWEwMjItNGFhZi05Y2U5LTQ2YzhiNzg0NzIzZSIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzA3NjU0MTc5LCJ1c2VySWQiOiI1MmNhOTdkYS1hMDIyLTRhYWYtOWNlOS00NmM4Yjc4NDcyM2UiLCJyb2xlIjoiIn0.CtukudEHliB5HGDhtowrtg-5TBq0JrwqUAbGyZyaN9Y"

# Ejecuta nuestra aplicación cuando se inicia el contenedor
CMD ["python", "app_waitress.py"]
