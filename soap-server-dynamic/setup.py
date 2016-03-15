from setuptools import setup, find_packages
import os

setup(
      name='Dynamic Soap Server',
      version='1.0',
      description='Auto-generated Soap Server to dispatch SOAP request to rest services',
      author='Eric Engstfeld and Leonardo G. Leenen',
      author_email='eric@moorea.io, leonardo.leenen@agtech.com.ar',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['flask','flask_cors','httplib2','pysimplesoap', 'flask-spyne','lxml','spyne', 'jinja2']
)

