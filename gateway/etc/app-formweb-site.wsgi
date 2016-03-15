import sys
import os
import site

from os import environ, getcwd
import logging, sys

  

sys.path.append("/home/b996031/moorea/instance_config/gateway/gateway/src")
os.environ['PYTHON_EGG_CACHE']="/usr/lib64/python2.7/site-packages"
os.environ['GATEWAY_SETTINGS']="/home/b996031/moorea/instance_config/gateway/gateway.cfg" 
site.addsitedir('/usr/lib64/python2.7/site-packages')

from runserver import app as application

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

LOG = logging.getLogger(__name__)
LOG.debug('Current path: {0}'.format(getcwd()))

# Application config
application.debug = True



with application.app_context():
	pass
