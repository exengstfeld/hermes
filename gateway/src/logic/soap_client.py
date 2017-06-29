#!/usr/bin/python
# -*- coding: latin-1 -*-


'''
SOAP Client
Dispatchs request to a configured SOAP SERVER instance. Refer to README documentation for more information of its functionalities
@author: Eric Engstfeld
'''

from flask import current_app, session
from pysimplesoap.client import SoapClient, SoapFault
from pysimplesoap.simplexml import SimpleXMLElement
import dicttoxml
from bson.json_util import dumps
import json
import sys
from base64 import b64encode

class CommunicationException(Exception):
	_message=""
	def __init__(self, msg):
		self._message = msg

def dispatch(path, request, service):
    '''
        Dispatchs the given request to the given configured soap service
        @author: Eric Engstfeld
    '''
    current_app.logger.debug('Request header content type is \n' + str(request.headers.get("Content-Type")))
    current_app.logger.debug('Request data is \n' + str(request.data))
    get_parsed_request_data = lambda req: ("x-www-form-urlencoded" in str(req.headers.get("Content-Type")).strip() and reduce(lambda a,b : (a in req.form and a+"="+ req.form[a] +"&"+b+"="+ req.form[b]) or a+"&"+b+"="+ req.form[b], req.form)) or dumps(req.data)
    data = get_parsed_request_data(request)
    response = call(service["soap_method"], request.method, path, request.headers.get("Content-Type"), request.headers, data)
    current_app.logger.debug('Service response is\n' + str(response))
    return response

def call(soap_method, method, path, ct, params, data):
    '''
        Calls SOAP SERVER based on given params and service.
        @author: Eric Engstfeld
    '''
    try:
        current_app.logger.debug("Calling soap server with: method:{0} path:{1} ct:{2} params:{3} data:{4}".format(method, path, ct, params, data))
        headers = json.loads(dumps(params))
        if session.get("user") != None and session.get("user").get("token") != None:
            headers["Authorization"] = session["user"]["token"]
        client = get_client()
        soap_function = getattr(client, soap_method)
	data = b64encode(data)
        response = soap_function(web_method=method, url_pattern=path, content_type=ct, params=dumps(headers), raw=data, location=current_app.config["APPLICATION"])    
        result = getattr(response, soap_method+"Result")
        return result
    except AttributeError, e:
        current_app.logger.exception(e)
        raise CommunicationException("El metodo soap que se desea invocar no existe. Por favor revise su configuracion. Mensaje: "+ str(e)) 
    except Exception, e:
        current_app.logger.exception(e)
        raise CommunicationException("Ha ocurrido un error en la comunicacion con los servicios. Es posible que no disponga de los permisos suficientes o bien, se encuentren caidos. Por favor, contacte a su administrador. Mensaje: \n"+ str(response)) 

def get_client():
    '''
        Gets ANSES Director SOAP client normalized with required headers
        @author: Eric Engstfeld
    '''
    client = SoapClient(namespace=current_app.config['NAMESPACE'],action=current_app.config['ACTION'],location=current_app.config['LOCATION'], soap_ns=current_app.config['SOAP_NS'], trace = current_app.config['TRACE'], ns = current_app.config['NS'], exceptions=current_app.config['EXCEPTIONS'])
    if not current_app.config["DEV_MODE"]:
        header = SimpleXMLElement('<Headers/>', namespace=current_app.config['NAMESPACE'])
        token = header.add_child("token", text=session["data"]["token"])
        token['xmlns']=current_app.config['CREDENTIALS_XMLNS']
        sign = header.add_child("sign", text=session["data"]["sign"])
        sign['xmlns']=current_app.config['CREDENTIALS_XMLNS']
        client['token']=token
        client['sign']=sign
    return client

def get_roles_matrix():
    '''
        Gets ANSES Director ROLES x FUNCTIONALITIES matrix based in configured ANSES ROLES SOAP Client
        @author: Eric Engstfeld
    '''
    client = SoapClient(wsdl=current_app.config["ANSES_ROLES_MATRIX_WSDL"], soap_ns=current_app.config['ANSES_ROLES_MATRIX_SOAP_NS'], trace = current_app.config['ANSES_ROLES_MATRIX_TRACE'], ns = current_app.config['ANSES_ROLES_MATRIX_NS'], exceptions=current_app.config['ANSES_ROLES_MATRIX_EXCEPTIONS'],proxy=current_app.config['ANSES_ROLES_MATRIX_PROXY'])
    response = client.GetGrantFromSystemGroup(system=session["user"]["system"], group=session["user"]["user_profiles"][0]['profile_id'])
    current_app.logger.debug(response)
    return response


################
#   HELPERS
################

def find_service(path, method):
    '''
        Finds an associated service to the given path, if not found returns None
        @author: Eric Engstfeld
    '''
    for service in filter(lambda x: x['method'] == method, current_app.config['SERVICES']):
        if (is_alike(service['pattern'].split('/'), path.split('/'))): return service
    return None

def is_alike(spattern, spath):
    '''
        This method does the pattern matching.
        If the given splitted pattern is alike the splitted path, returns True
        @author: Eric Engstfeld
    '''
    if len(spattern) != len(spath): return False
    for inx, elem in enumerate(spattern):
        if (elem == current_app.config['WILDCARD']): break
        if not (elem == spath[inx]): return False
    return True

################
#  CLASSES
################

class ParamsBuilder:
    '''
        UNUSED!
        Params builder has the logic associated to the different params types and their actions
        @author: Eric Engstfeld
    '''
    
    DEFAULT_XML_HEADER = '<?xml version="1.0" encoding="UTF-8" ?>'
    PARAM_FORM_TYPE = 'FORM'
    PARAM_JSON_TYPE = 'JSON'
    PARAM_PATH_TYPE = 'PATH'

  
    def build(self, request, spath, params, method):
        basic = self.DEFAULT_XML_HEADER+"<"+method+">"
        current_app.logger.debug('Building params for the path \n' + str(spath) + '\n for params \n' + dumps(params) + ' \n and request ' + str(request))
        for param in params:
            if param['type'] == self.PARAM_PATH_TYPE: basic += self.path_param_to_xml(spath, param)
            if param['type'] == self.PARAM_JSON_TYPE: basic += self.json_data_to_xml(param, json.loads(request.data))
            if param['type'] == self.PARAM_FORM_TYPE: basic += self.form_data_to_xml(request.form)
        basic +=  "</"+method+">"
        return basic

    def json_data_to_xml(self, param, data):
        return dicttoxml.dicttoxml(data, attr_type=False, root=False)#.replace(self.DEFAULT_XML_HEADER, '', 1)

    def form_data_to_xml(self, data):
        return reduce(lambda a, b: '<' + a + '>' + data[a] + '</' + a + '>' + '<' + b + '>' + data[b] + '</' + b + '>', data.keys())

    def path_param_to_xml(self, spath, param):
        return '<' + param['name'] + '>' + spath[param['position']] + '</' + param['name'] + '>'
