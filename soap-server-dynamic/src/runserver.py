#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# -*- coding: utf-8 -*-         
#!/usr/bin/python
# -*- coding: ascii -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding: latin-1 -*-
#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from jinja2 import Template, Environment, FileSystemLoader
from flask import Flask, current_app, jsonify, render_template, request, url_for, redirect, flash, session, make_response
from flask_cors import cross_origin
import json
from functools import wraps
import os
import uuid
import json
from pymongo import MongoClient
from flask.ext.spyne import Spyne
from spyne.protocol.soap import Soap11
from spyne.model.primitive import Unicode, Integer
from spyne.model.complex import Iterable
import httplib2 as http
import sys
from pysimplesoap.client import SoapClient, SoapFault
from pysimplesoap.simplexml import SimpleXMLElement
from base64 import b64decode
from bson.json_util import dumps

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = Flask("dynamic-soap-server")
app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"

is_str = lambda s: isinstance(s, unicode) or isinstance(s, str)
str_to_obj = lambda s, f: (is_str(s) and f(json.loads(s), str_to_obj)) or s

spyne = Spyne(app)

try:
    app.config.from_envvar('SOAPSERVER_SETTINGS')
except Exception, e:
    print "Lo sentimos, pero no se encuentra la referencia a la variable de ambiente SOAPSERVER_SETTINGS la cual debe estar definida y poseer el archivo de configuracion correspondiente"
    sys.exit(-1)

reload(sys)
sys.setdefaultencoding("utf-8")

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('runserver.py')
soap_server_code = template.render(external_services=app.config["EXTERNAL_SERVICES"], services=app.config["SERVICES"], namespace=app.config["NAMESPACE"],soap_location=app.config["SERVICE_LOCATION"],soap_validator=app.config["VALIDATOR"])
exec(soap_server_code)

@app.route("/") 
def index(): 
		return "esto parece que funca" 

if __name__ == '__main__':
	app.debug=False
	app.run("0.0.0.0",app.config["PORT"]) 
