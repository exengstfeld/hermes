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

from flask import Flask, current_app, jsonify,Response, render_template, request, url_for, redirect, flash, session, make_response
from functools import wraps
from flask_cors import cross_origin
from bson.json_util import dumps
import os
import json
import sys
from datetime import datetime, date
import time
import xml.etree.cElementTree as ET
from logic import soap_client as sc
from logic.soap_client import CommunicationException
from M2Crypto import X509
from base64 import b64decode
import uuid
import base64
import shelve

class MyFlask(Flask):
    @property
    def static_folder(self):
        if self.config.get('HTML_FOLDER') is not None:
            return os.path.join(self.root_path, self.config.get('HTML_FOLDER'))
    @static_folder.setter
    def static_folder(self, value):
        print value
    @property
    def template_folder(self):
        if self.config.get('HTML_FOLDER') is not None:
            return os.path.join(self.root_path, self.config.get('HTML_FOLDER'))
    @template_folder.setter
    def template_folder(self, value):
        print value

app = MyFlask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

try:
    app.config.from_envvar('GATEWAY_SETTINGS')
except Exception, e:
    print "Lo sentimos, pero no se encuentra la referencia a la variable de ambiente GATEWAY_SETTINGS la cual debe estar definida y poseer el archivo de configuracion correspondiente"
    sys.exit(-1)

reload(sys)
sys.setdefaultencoding("utf-8")

class SecurityException(Exception):
    _message=""
    def __init__(self, msg):
        self._message = msg

def logged_in(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if (current_app.config["DEV_MODE"] or (session.get('data') is not None and session.get("user") is not None)):
                current_app.logger.debug("User is logged in or in dev_mode...")
		try:
			validate_token_and_sign(session["data"]["token"], session["data"]["sign"])
		except SecurityException, se:
			return redirect(current_app.config["LOGIN_URL"], 302)
                return f(*args, **kwargs)
            else:
                current_app.logger.debug("User is not logged in, redirecting...")
                return redirect(current_app.config["LOGIN_URL"], 302)
        return decorated_function



def token_validation(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config["DEV_MODE"] and session.get('data') is not None:
                validate_token_and_sign(session["data"]["token"], session["data"]["sign"])
                return f(*args, **kwargs)
        return decorated_function


@app.route("/fs/raw/<file_st>", methods=['POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
def bucket_add_raw_file(file_st):
        path = ""

        if file_st == "bucket":
                path = current_app.config['FILE_STORAGE_BUCKET']

        if path == "":
                return jsonify(success=False, result="Lo sentimos pero el repositorio solicitado no existe"), 422
        try:
                file_stored = []
                file = request.files.get("file")
                key = add_raw_file(base64.b64encode(file.read()), path)
                return jsonify(success=True, result=key)
        except Exception, ex:
                current_app.logger.exception(ex)
                return jsonify(success=False, result="Ha ocurrido un error al agregar el archivo"), 500

@app.route("/fs/bucket/<id>", methods=["DELETE"])
@cross_origin(headers=['Content-Type', 'Authorization'])
def bucket_del_file(id):
   
    result = del_file(str(id), current_app.config['FILE_STORAGE_BUCKET'])

    if result is False: 
        return jsonify(success=False, result="El archivo solicitado no ha sido localizado"), 422
    else:
        return jsonify(success=True, result="La operacion se ha realizado con exito"), 200


@app.route('/<path:path>', methods=['POST','GET','PUT','DELETE'])
@logged_in
def catch_all(path):
        current_app.logger.debug("Request PATH = " + path + " | METHOD = " + request.method)
        service = sc.find_service(path, request.method)
        if service == None:
            return app.send_static_file(path)
        else:
            try:
                current_app.logger.debug(service)
                result = sc.dispatch(path, request, service)
                current_app.logger.debug(result)
                return Response(response=str(result), status=200, mimetype="application/json")
            except CommunicationException, ce:
                app.logger.exception(ce)
                return jsonify(success=False, msg="Error de comunicacion. Verifique la conexion con los servicios", data=str(ce)), 500
            except SecurityException, se:
                app.logger.exception(se)
                return jsonify(success=False, msg="Error de seguridad. Verifique sus credenciales", data=str(se)), 403
            except Exception, e:
                app.logger.exception(e)
                return jsonify(success=False, msg="Error en el servidor", data=str(e)), 500

def to_json(a, b):
	if b == None or b == "" or len(b) < 3:
		return a
	base = {}
	splitted_b = b.split("=")
	if isinstance(a, str) or isinstance(a, unicode):
		splitted_a = a.split("=")
		if a[0] != "#" and len(splitted_a) == 2:
			aux={}
			aux[splitted_a[0]] = splitted_a[1].replace('"','').replace("'","")
			a = aux
	if b[0] != "#" and len(splitted_b) == 2:
		base[splitted_b[0]] = splitted_b[1].replace('"','').replace("'","")
	if a != None:
		return {key: value for (key, value) in (a.items() + base.items())}
	else:
		return base
			

@app.route("/", methods=['POST'])
@cross_origin(headers=['Content-Type'])
def autentication_with_token_and_sign():
    try:
        current_app.logger.debug("Saving TOKEN and SIGN in session") 
        session['data'] = {'token':request.form.get('token'), 'sign':request.form.get('sign'), 'action':request.form.get('action'), 'formid': request.form.get('formid')}
        
        current_app.logger.debug("Validating token and sign...") 
        validate_token_and_sign(session['data']['token'], session['data']['sign'])
        
        current_app.logger.debug("Parsing user data...")
        session["user"] = parse_user_data(ET.fromstring(b64decode(session['data']["token"])))
        # session["user"]["extra_data"] = get_employee_extra_data()
        token = load_secure_services()

        #ini = { "cfg": load_initial_configuration() }
	
	config = load_initial_configuration()
	config_decoded = b64decode(config)

        ini = reduce(lambda a, b: to_json(a,b), config_decoded.split("\n"))
	#ini = load_initial_configuration()

        if session['data'].get('formid'):
            goto = current_app.config['FLOW_EXECUTION_URL']+ "/" + session['data'].get('formid')
            redirect_to = redirect(goto)
            response = current_app.make_response(redirect_to)
            response.set_cookie('token_id',value=str(token))
            response.set_cookie('token_imanager',value=str(token))
            return response,302

        else:
	    response = current_app.make_response(render_template("index.html", ini=ini))
            response.set_cookie('token_id',value=str(token))
            response.set_cookie('token_imanager',value=str(token))
            current_app.logger.debug("Finished with success!! returning INDEX...") 
            return response

    except CommunicationException, ce:
        app.logger.exception(ce)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_FORBIDDEN"])), 500
    except SecurityException, se:
        app.logger.exception(se)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_FORBIDDEN"])), 403
    except Exception, e:
        app.logger.exception(e)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_GENERIC"])), 500

@app.route("/")
@logged_in
def redirect_to_login_url():
    try:
        if current_app.config["DEV_MODE"]:
            current_app.logger.debug("Dev mode is active, checking session...")
            session['data'] = current_app.config["DEV_MODE_TOKEN"]
            session["user"] = current_app.config["DEV_MODE_USER"]

        # session["user"]["extra_data"] = get_employee_extra_data()
        token = load_secure_services()
        ini = {"cfg": load_initial_configuration()}
        response = current_app.make_response(render_template("index.html", ini=ini))

        if session['data'].get('formid'):
            # response with iframe url
            pass
            
        response.set_cookie('token_id',value=token)
        response.set_cookie('token_imanager',value=token)
        return response
    except CommunicationException, ce:
        app.logger.exception(ce)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_FORBIDDEN"])), 500
    except SecurityException, se:
        app.logger.exception(se)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_FORBIDDEN"])), 403
    except Exception, e:
        app.logger.exception(e)
        return current_app.make_response(render_template(current_app.config["STANDALONE_HTML_GENERIC"])), 500

@app.route("/security/matrix", methods=["GET"])
@logged_in
def get_available_functionalities():
    try:
        matrix = sc.get_roles_matrix()["GetGrantFromSystemGroupResult"]
	
        return jsonify(success=True, result=current_app.config["ANSES_ROLES_MATRIX_PARSER"](matrix))
    except Exception, ex:
        current_app.logger.exception(ex)
        return jsonify(success=False, msg="Ha ocurrido un error en el servidor", data=str(ex)), 500

@app.route('/ping')
def ping():
    current_app.logger.debug("Everything is OK")
    return "Everything is OK"

@app.route('/logout')
def logout():
    session["data"] = None	
    session["user"] = None
   # must call to sucurity_bp and remove token?
    return "Ha finalizado su sesion"

# HELPERS

def is_static(path):
    for end in current_app.config["KNOWN_STATICS"]: 
        if path.endswith(end): return True
    return False

def validate_token_and_sign(token, sign):
    if current_app.config["ANSES_TOKEN_VALIDATIONS_ENABLED"]:
        current_app.logger.debug("TOKEN and SIGN validation is enabled. Doing it ...")
        
        # Verify IP
        ip_validation = lambda token_xml, ip: next(info for info in token_xml.iter("info") if info.attrib['name'] == "ip").attrib['value'] != ip
        if ip_validation(ET.fromstring(b64decode(token)), request.remote_addr): raise SecurityException(current_app.config["VALIDATION_IP_MSG"])

        # Verify EXPIRATION
        token_expiration_validation = lambda token_xml, time: long(next(id_tag for id_tag in token_xml.iter("id")).attrib["exp_time"]) < time
        if token_expiration_validation(ET.fromstring(b64decode(token)), time.time()): raise SecurityException(current_app.config["VALIDATION_EXPIRATION_MSG"])

        # Verify SIGN
        pubkey = X509.load_cert(current_app.config["VALIDATION_SIGN_CERT_PATH"]).get_pubkey()
        pubkey.reset_context(md='sha1')
        pubkey.verify_init() 
        pubkey.verify_update(str(b64decode(token)))
        if pubkey.verify_final(b64decode(sign)) != 1: raise SecurityException(current_app.config["VALIDATION_SIGN_MSG"])


def parse_user_data(root):
    user = {"extra_data":None, "roles":[],"organization":current_app.config["FIXED_ORGANIZATION_ID"] , "payload":{"organization":current_app.config["FIXED_ORGANIZATION_ID"]}}
       
    uid = ''
    entity = ''
    system = ''
    username = ''
    authmethod = ''
    nombre = ''
    email = ''
    oficina = ''
    oficinadesc = ''
    ou = ''


    for child in root.iter('login'):
       
        user['uid'] = child.attrib['uid']
        
        uid = child.attrib['uid']
        entity = child.attrib['entity']
        system = child.attrib['system']
        username = child.attrib['username']
        authmethod = child.attrib['authmethod']

        user['system'] = child.attrib['system']
        user['organization'] = {'organization_id':  child.attrib['system'],'organization_description':  child.attrib['system'] }
        user["payload"]['organization'] = {'organization_id':  child.attrib['system'],'organization_description':  child.attrib['system'] }
        
        for child in root.iter('info'):
   
            if (child.attrib['name'] == current_app.config["TOKEN_ATTR_CN"]):
                user['cn'] = child.attrib['value']

            if (child.attrib['name'] == current_app.config["MAIL_ATTR"]):
                user['email'] = child.attrib['value']

            if (child.attrib['name'] == 'nombre'):
                nombre = child.attrib['value']

            if (child.attrib['name'] == 'email'):
                email = child.attrib['value']

            if (child.attrib['name'] == 'oficina'):
                oficina = child.attrib['value']

            if (child.attrib['name'] == 'oficinadesc'):
                oficinadesc = child.attrib['value']

            if (child.attrib['name'] == 'ou'):
                ou = child.attrib['value']

	user["user_profiles"] = []
	user["roles"] = []

    for group in root.iter('group'):
            user["user_profiles"].append({"profile_id": group.attrib["name"], "profile_description":group.attrib["name"]})
	
    for group in root.iter('group'):
            user["roles"].append({"rol_id": group.attrib["name"], "rol_description":group.attrib["name"]})
    
    # ROLES

    # SI EL PERFIL ES DISTINTO DE Administrador, Operador y Publicador, EL ROL ES IGUAL AL PERFIL
    if user["user_profiles"][0]['profile_id'] != 'Administrador' and user["user_profiles"][0]['profile_id'] != 'Operador' and user["user_profiles"][0]['profile_id'] != 'Publicador':
        user["roles"] = [{"rol_id": user["user_profiles"][0]['profile_id'], "rol_description":user["user_profiles"][0]['profile_id']}]    

    if authmethod == 'NTLM':
        if uid[:1].lower() == 'a':
            # Chequear META4 para ver si es personalsuperior. Si no lo es, es agente
            extra_data = get_employee_extra_data(uid[1:])

            if extra_data['txt_personal_superior'].lower() == 's':
                user["roles"] = [{"rol_id": 'INTRANET-RESPONSABLE', "rol_description":"Intranet - Responsable"}]    
            else:
                user["roles"] = [{"rol_id": 'INTRANET-AGENTE', "rol_description":"Intranet - Agente"}]    
            
            user["NivelSuperior"] = extra_data["txt_nivel_superior"]
            user["NivelUnidad"] = extra_data["txt_nivel_unidad"]


        if uid[:1].lower() == 'e':
            user["roles"] = [{"rol_id": 'INTRANET-AGENTE', "rol_description":"Intranet - Agente"}]    
    
    user['dependencia_cod'] = oficina
    user['dependencia_desc'] = oficinadesc
    user['ou'] = ou

    user['office_id'] = ou.split(",")[0][0:10]
    user['office_desc'] = ou.split(",")[0][10:]

    if current_app.config.get("FILTER_BY_OU"):
        user['organization'] = {'organization_id': user['office_id'] ,'organization_description': user['office_desc']}
        user["payload"]['organization'] = {'organization_id':  user['office_id'],'organization_description':  user['office_desc'] }

    return user

def get_employee_extra_data(legajo):
    '''
        GETS employee extra data based on token LEGAJOID session["user"] must be loaded first
        @raises: Exception if fails, else @returns: extra_data
    '''
    current_app.logger.debug("Calling employee extra data services...")
    response = sc.call(current_app.config["EMPLOYEE_EXTRA_DATA_METHOD"], "", "", "", {}, dumps({ "legajo" : legajo}))
    current_app.logger.debug(response)
    extra_data = json.loads(str(response))
    current_app.logger.debug("Retrieving extra user data...")
    return extra_data

def load_secure_services():
    '''
        Load secure services data if module is enabled. Must be an user loaded on session["user"]
        @raises: Exception if fails, else @returns: token
    '''
    if current_app.config["SECURE_SERVICES_ENABLED"]:
        current_app.logger.debug("Calling secure services...")
        session["user"]["one_shoot"] = False

        session["user"]["token_and_sign"] = {}
        session["user"]["token_and_sign"]["token"] = session["data"]["token"]
        session["user"]["token_and_sign"]["sign"] = session["data"]["sign"]

        scp_response = sc.call("CreateSessionToken", "POST", current_app.config["SECURE_SERVICES_PATH"], "application/json;charset=UTF-8", {}, dumps(session["user"]))
        current_app.logger.debug(scp_response)
        result = json.loads(str(scp_response))
        current_app.logger.debug(result)
        current_app.logger.debug("Saving user data in session...")
        if result["success"]:
            session['user']["token"] = result["result"]["token"]
            return result["result"]["token"]
        else:
            raise Exception(result["msg"]) 
    return ""

def load_initial_configuration():
    '''
        Loads initial configuration if module is enabled. 
        @returns: app configuration
    '''
    if current_app.config["INITIAL_CONFIGURATION_ENABLED"]:
        current_app.logger.debug("Retrieving APP configuration...") 
        config_response = json.loads(str(sc.call("GetConfig", "GET", current_app.config["INITIAL_CONFIG_PATH"], "application/json;charset=UTF-8", {}, "{}")))
        current_app.logger.debug(config_response)
        return config_response["result"]
    return {}


def add_raw_file(file_content64, file_storage):
        '''
        Add a file given a file_storage. Exceptions are unhandled
        '''
        bucket = shelve.open(file_storage)
        key = str(uuid.uuid4())
        bucket[key] = file_content64
        bucket.close()
        return key

def add_file(message, file_storage):
        '''
        Add a file given a file_storage. Exceptions are unhandled
        '''
        file_stored = []
        bucket = shelve.open(file_storage)

        for msg in  message["files"]:
                key = str(uuid.uuid4())
                bucket[key] = msg
                file_stored.append({"file_name":msg["file_name"], "key":key})

        bucket.close()
        return file_stored

def del_file(id, file_storage_path):
    '''
    Delete a file from storage given an id. Exceptions are unhandled
    '''
    bucket = shelve.open(file_storage_path)

    if bucket.has_key(id) is False: 
        bucket.close()
        return False

    result = bucket[id]
    del bucket[id]
    return True





######################################################
if __name__ == '__main__'  :
    with app.app_context():
        '''App Conext Here'''
    app.debug = False
    app.run("0.0.0.0", app.config["PORT"])
