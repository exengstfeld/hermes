from setuptools import setup, find_packages
import os

setup(
      name='Gateway',
      version='1.0',
      description='Gateway solution to adapt a front app to ANSES security schema',
      author='Eric X. Engstfeld',
      author_email='eric@moorea.io',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['flask','M2Crypto', 'flask_cors', 'httplib2', 'pysimplesoap', 'dicttoxml']
)

