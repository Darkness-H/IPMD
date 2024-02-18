# Libreria para aplicaciones web
from flask import Flask
# Libreria para realizar conexiones con servidores Redis
from redis import Redis, RedisError
# Libreria para utilizar funciones de Operating System
import os
import socket
# Libreria para realizar peticiones a traves de las APIs
import requests

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

# Create a Flask instance named app
app = Flask(__name__)

# Variable de entorno para AEMET, si la clave de defecto no funciona podemos pasarle al programa una nueva por el terminal
API_KEY_DEFAULT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDMxNDM5NjA1QHFxLmNvbSIsImp0aSI6IjUyY2E5N2RhLWEwMjItNGFhZi05Y2U5LTQ2YzhiNzg0NzIzZSIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzA3NjU0MTc5LCJ1c2VySWQiOiI1MmNhOTdkYS1hMDIyLTRhYWYtOWNlOS00NmM4Yjc4NDcyM2UiLCJyb2xlIjoiIn0.CtukudEHliB5HGDhtowrtg-5TBq0JrwqUAbGyZyaN9Y"
API_KEY = os.environ.get('AEMET_API_KEY', API_KEY_DEFAULT)

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(),  visits=visits)

@app.route("/test")
def test():
    html = "<h3>Testing </h3>" \
           "<b>Status:</b> OK"
    return html

@app.route("/trafico/<airport>")
def trafico(airport):
    # Valores disponibles para airport (mayúsculas o minúsculas)
    airports = ['A-1', 'AP-1', 'A-8', 'AP-68', 'A-15']

    # Función que devuelve el último parte de incidencias de tráfico en la autopista seleccionada
    def make_request(airport):

        # Pedimos información a través de una API
        response = requests.get('https://api.euskadi.eus/traffic/v1.0/incidences?_page=1')
        data = response.json()

	# Obtener todas las incidencias de la página 1
        # Las incidencias están ordenadas de manera que los objetos de menor índice son los más recientes
        incidences = data['incidences']

	# Guardaremos la incidencia en la variable obj
        obj = None

	# Iterar sobre las incidencias y extraer la última información de la autopista seleccionada
        for incidence in incidences:

	    # Salimos del bucle si encontramos la instancia más reciente
            if (airport.lower() == incidence['road'].lower()):

                obj = incidence
                break

        return obj

    # Función que imprime los mensajes correspondientes
    def get_info(airport, airports=airports):

        # Comprobamos la validez del aeropuerto
        if (airport.upper() in airports):

	    # obtenemos la instancia objetivo
            obj = make_request(airport)

	    # Si en la primera página no se encuentra ninguna instancia de la autopista seleccionada
            if (obj == None):

                return f"There are no recent incidences about the airtport: {airport.upper()}"

            else:

                return obj

        else:

	    # En el caso de que el aeropuerto introducido no es válido
    	    return f"Please enter one of the following airports"

    obj = get_info(airport)

    if (isinstance(obj,str)):

        html = "<h3>Trafico</h3>" \
           	"<b>Mensaje:</b> {message}<br/>" \
           	"<b>Valores validos:</b> {airports}"

        return html.format(message=obj,  airports=airports)

    else:

        html = "<h3>Trafico</h3>" \
		"<b>Mensaje:</b> Datos de la última parte de incidencias de tráfico en la autopista {autopista}<br/>" \
		"<b>Datos:</b><br/>"

	# Iterate over the key-value pairs in the obj
        for key, value in obj.items():

            # Add each key-value pair to the HTML string
            html += f"<b>{key}:</b> {value}<br/>"

        return html.format(autopista=airport.upper())

@app.route("/tiempo/<city>")
def tiempo(city):
    # Valores disponibles para city (mayúsculas o minúsculas)
    cities = ["Bilbao", "Donostia", "Vitoria"]

    # Función que devuelve la última predicción de temperaturas máximas y mínimas para la ciudad seleccionada
    def make_request_weather(city, cities=cities, API_KEY=API_KEY):

        # Parámetros de consulta con la API key
        params = {'api_key': API_KEY}

        # Cada ciudad tiene un ID para acceder a su fichero json
        if (city == cities[0]):
            id = "48020"
        elif (city == cities[1]):
            id = "20069"
        else:
            id = "01059"

        # Pedimos información a través de una API
        response = requests.get('https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/' + id, params=params)
        data = requests.get(response.json()['datos'], params=params).json() # response.json()['datos'] Devuelve una API para acceder a los datos de la ciudad seleccionada

        # Obtenemos la última predicción de temperaturas
        max, min = data[0]['prediccion']['dia'][-1]['temperatura']['maxima'], data[0]['prediccion']['dia'][-1]['temperatura']['minima']

        return max, min

    # Función que imprime los mensajes correspondientes
    def get_info_weather(city, cities=cities, API_KEY=API_KEY):

        # Ajustamos el nombre de la ciudad
        if (len(city) > 2):
            city_aux = city[0].upper() + city[1:].lower()
        else:
            city_aux = "None"

        # Comprobamos la validez de la ciudad
        if (city_aux in cities):

            # obtenemos la instancia objetivo
            max, min = make_request_weather(city_aux)
            return max, min

        else:

            # En el caso de que la ciudad introducida no es válida
            return  None, None

    max, min = get_info_weather(city)

    if (max == None and min == None):

        html = "<h3>Tiempo</h3>" \
                "<b>Mensaje:</b> Please enter one of the following cities<br/>" \
                "<b>Valores validos:</b> {cities}"

        return html.format(cities=cities)

    else:

        html = "<h3>Tiempo</h3>" \
                "<b>Mensaje:</b> Previsión de temperaturas en {city}<br/>" \
                "<b>Maxima:</b> {max}<br/>" \
                "<b>Minima:</b> {min}"

        return html.format(city=city[0].upper() + city[1:].lower(),max=max,min=min)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=696)
