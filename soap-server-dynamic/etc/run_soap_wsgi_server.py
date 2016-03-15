import logging
logging.basicConfig(level=logging.DEBUG)

from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode

from spyne.model.complex import Iterable

from spyne.protocol.soap import Soap11

from spyne.server.wsgi import WsgiApplication

class HelloWorldService(ServiceBase):
	@srpc(Unicode, Integer, _returns=Iterable(Unicode))
	def say_hello(name, times):
		for i in range(times):
			yield 'Hello, %s' % name

	@srpc()
	def isalive():
		print "Solo estoy vivo :-)" 


application = Application([HelloWorldService],
				tns='spyne.examples.hello',
				in_protocol=Soap11(validator='lxml'),
				out_protocol=Soap11()
				)

if __name__ == '__main__':
	# You can use any Wsgi server. Here, we chose
	# Python's built-in wsgi server but you're not
	# supposed to use it in production.
	from wsgiref.simple_server import make_server

	wsgi_app = WsgiApplication(application)
	#wsgi_app.doc.wsdl11.build_interface_document("http://10.0.1.25")

	server = make_server('0.0.0.0', 4500, wsgi_app)
	server.serve_forever()
