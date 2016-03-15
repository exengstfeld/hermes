Author: Eric Engstfeld

Date: 28 de Agosto, 2015

# SOAP Server

# Abstract

La finalidad de este documento consiste en exponer cómo está construído el componente SOAP Server, los pasos para su instalación, su adecuada configuración y detallar sus funcionalidades principales y características para una futura extensión y reutilización por parte de otros componentes. Al final del mismo se encontrará una sección de glosario explicando aquellos términos técnicos que ameritan aclaración y a su vez otra de contacto con los datos de sus desarrolladores en caso de dudas o sugerencias.
 
<span id="0"/></span>

# Index

1. [Introducción](#1)
2. [Librerías](#2)
3. [Pre-Requisitos](#3)
4. [Instalación](#4)
5. [Consideraciones especiales](#5)
	- [Instalación en ambiente productivo](#51)
6. [Mantenimiento](#6)
7. [Glosario](#7)
8. [Contacto](#8)


<span id=“1”/></span>
# Introducción
El SOAP Server junto al Gateway forman parte de la solución de adaptar una aplicación web con un front y back de protocolo REST como comunicación a la arquitectura demandada por ANSES y la conexión al Director. En este caso, el SOAP Server, se encarga específicamente de recibir los request REST a los diferentes métodos expuestos y redirigirlos intactos a la aplicación BACKEND correspondiente. Los servicios que se exponen en la especificación (WSDL) son dinámicos y cargados en base al archivo de configuración detallado más adelante. Es decir, está preparado para exponer N servicios SOAP teniendo cada uno un servicio de BACKEND independiente para su redirección, esto es posible utilizando templating detallado también más adelante en la sección Mantenimiento. 

<span id=“2”/></span>
# Librerías
El lenguaje utilizado es Python 2.7 conteniendo a su vez las siguientes librerías disponibles en su repositorio (https://pypi.python.org/):

* [Flask](https://pypi.python.org/pypi/Flask)
* [flask-spyne](https://pypi.python.org/pypi/flask-spyne)
* [flask_cors](https://pypi.python.org/pypi/Flask-Cors)
* [httplib2](https://pypi.python.org/pypi/httplib2)
* [spyne](https://pypi.python.org/pypi/spyne)
* [lxml](https://pypi.python.org/pypi/lxml)
* [jinja2](https://pypi.python.org/pypi/jinja2)

<span id=“3”/></span>
# Pre-Requisitos

1. Para ambiente productivo:
	* Python 2.7
	* Apache2
2. Para ambiente de desarrollo:
	* Python 2.7

<span id=“4”/></span>

# Instalación
Ingresar al directorio raiz del proyecto soap-server-dynamic y ejecutar el setup.py para instalar las librerías:

<pre>
python setup.py build
python setup.py develop
</pre>

Una vez instaladas las librerías podremos ejecutar el código, pero antes de ello debemos armar nuestro propio archivo de configuración para adaptarlo a nuestro entorno. Copiamos alguno de ejemplo desde el directorio /etc y lo editamos:

<pre>
cp etc/soapserver.cfg /my/proyect/configuration/path/
vim /my/proyect/configuration/path/soapserver.cfg
</pre>

A continuación detallaremos cada una de las secciones del mismo para facilitar y hacer más amena esta tarea:

~~~~~~
**Keys that will be inserted on template. Strings must have double quotes ("'example'") the others just one.**
NAMESPACE="'http://ansesarg.anses.gov.ar'"	-> Namespace a utilizar por los servicios
SERVICE_LOCATION="'/soap/retrieve'"	-> Ubicación del servicio SOAP
VALIDATOR="None"	-> Validador del schema SOAP con el cual se comunicará. Por defecto es "None"
SERVICES=[	-> Servicios que se deseen exponer en el WSDL, cada uno debe contener un nombre del metodo SOAP y la URL a invocar para redirigir el request REST
        {
                "function":"to_json",
                "location":"'http://localhost:4000/'"
        },{
                "function":"chicocana",
                "location":"'http://localhost:4000/'"
        }
]

## App configuration
PORT=4501	-> Puerto donde correrá la aplicación en caso de ejecutarse como standalone


EXTERNAL_SERVICES=[
	{
		"function":"get_office_children",
		"namespace":"'http://ansesarg.anses.gov.ar'",
		"wsdl":"'http://ansesnegodesapp/BUSS/Anses.BUSS.EmpleadosUnidadOrganica.Servicio/EmpleadoUnidadOrganicaWS.asmx?wsdl'",
		"soap_ns":"'soapenv",
		"trace":"True",
		"ns":"''",
		"exceptions":"True",
		"soap_attributes":"codigoUnidad=data.get('codigo_unidad')",
		"soap_method":"obtenerUnidadesOrganicasDependientesDirectas",
		"response_parser":"lambda response: response.obtenerUnidadesOrganicasDependientesDirectasResult"
	}
]	-> Servicios externos para hacer de proxy. Si necesita consultar algún servicio SOAP de ANSES desde el FRONT puede hacerlo adicionando aquí sus datos junto a una función de parseo que debe transformar su respuesta para ser finalmente de utilidad 
~~~~~~

Finalmente podremos correr nuestra aplicación exportando primero la variable de ambiente indicando la configuración a utilizar y luego ejecutando el componente:
<pre>
export SOAPSERVER_SETTINGS=/my/proyect/configuration/path/soapserver.cfg
python src/runserver.py
</pre>
Deberiamos ver el siguiente output:
<pre>
 * Running on http://0.0.0.0:4500/ (Press CTRL+C to quit)
 * Restarting with stat
</pre>
Felicidades, el SOAP Server está corriendo!
Puede visualizar el WSDL expuesto en http://localhost:4500/soap/retrieve?wsdl

<span id=“5”/></span>
# 5. Consideraciones especiales
En el siguiente apartado se encontrarán ciertas consideraciones especiales o problemas comunes a modo de consulta en caso de que se tope con alguna de ellas.

<span id=“51”/></span>
## 5.1 Instalación en ambiente productivo 
En un ambiente productivo debe tenerse en cuenta que el componente debe correr en un WEB SERVER. En este caso tomaremos como ejemplo [Apache2](http://python.org.ar/wiki/WSGI). Dentro de la raiz del proyecto encontrará un archivo .wsgi listo para ser integrado y configurado en el mismo. 

<span id=“6”/></span>
# 6. Mantenimiento
La funcionalidad principal de este componente reside en la utilización de templates a la hora de escribir cada método SOAP. Este template de métodos se puede cambiar y alterar en consecuencia todos los métodos SOAP expuestos. Para ello podremos editar el template ubicado en src/templates/runserver.py y adaptarlo a nuestro gusto. A continuación un ejemplo del mismo:

~~~~~~
class MethodsExpose(spyne.Service):
	__target_namespace__= {{namespace}}
	__service_url_path__ = {{soap_location}}
	__in_protocol__ = Soap11(validator={{soap_validator}})
	__out_protocol__ = Soap11()

	{% for service in services %}
	@spyne.srpc(Unicode,Unicode,Unicode,Unicode,Unicode,Unicode,_returns=Unicode)
	def {{service.function}}(url_pattern, content_type, web_method, params, raw, location):
		#try:
			h = http.Http(disable_ssl_certificate_validation=True)
			url = {{service.location}} + url_pattern
			app.logger.debug("Called URL "+ url)
			app.logger.debug("Params ")
			app.logger.debug( json.loads(params))


			data = b64decode(raw)
			if ((params is not None) and (json.loads(params).get("Content-Type") is not None) and ("json" in json.loads(params).get("Content-Type"))): 
				data=json.loads(data)
			app.logger.debug(data)
			response, content = h.request(url, web_method.strip(), data, headers=json.loads(params))			
			app.logger.debug("Response is "+ str(response)+ " and content is "+ str(content))
			return content
		#except Exception,ex:
		#	app.logger.exception(ex)
		#	return { "success": False, "data":str(ex), "msg":"Ha ocurrido un error en el servidor SOAP" }
	{% endfor %}
	
	{% for external_service in external_services %}
	@spyne.srpc(Unicode,Unicode,Unicode,Unicode,Unicode,Unicode,_returns=Unicode)
	def {{external_service.function}}(url_pattern, content_type, web_method, params, raw, location):
		app.logger.debug("Call {{external_service.function}} service With: url_pattern:{0} content_type:{1} web_method:{2} raw_data:{3} params:{4}".format(url_pattern,content_type,web_method,raw, params))			
		client = SoapClient(namespace={{external_service.namespace}}, wsdl={{external_service.wsdl}}, soap_ns={{external_service.soap_ns}}, trace = {{external_service.trace}}, ns = {{external_service.ns}}, exceptions={{external_service.exceptions}})
		data = str_to_obj(b64decode(raw), str_to_obj)
		response = client.{{external_service.soap_method}}({{external_service.soap_attributes}})
		app.logger.debug(response)
		parse = {{external_service.response_parser}}
		return dumps(parse(response))
	{% endfor %}

#obtenerEmpleadoLegajo legajo=data.get("legajo")

	@spyne.srpc(_returns=Unicode)
	def isalive():
		return "I'm Alive"   
~~~~~~

<span id=“7”/></span>
# 7. Glosario

* Gateway: El Gateway es otro componente dentro del mismo repositorio y solución que, junto al SOAP Server, proveen el módulo de seguridad completo para adaptar sus aplicaciones FRONT al esquema de seguridad de ANSES. Para más información consulte el README.md en la raiz de su directorio (source/gateway/)

<span id=“8”/></span>
# 8. Contacto
Si desea contactarse con el equipo por alguna duda o sugerencia puede realizarlo a través del siguiente e-mail: eric@moorea.io
