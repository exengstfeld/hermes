class MethodsExpose(spyne.Service):
	__target_namespace__= {{namespace}}
	__service_url_path__ = {{soap_location}}
	__in_protocol__ = Soap11(validator={{soap_validator}})
	__out_protocol__ = Soap11()

	{% for service in services %}
	@spyne.srpc(Unicode,Unicode,Unicode,Unicode,Unicode,Unicode,_returns=Unicode)
	def {{service.function}}(url_pattern, content_type, web_method, params, raw, location):
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

	@spyne.srpc(_returns=Unicode)
	def isalive():
		return "I'm Alive"  
