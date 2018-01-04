import os
import re
from setuptools import setup

from setup_helpers import find_version, read


_here = os.path.abspath(os.path.dirname(__file__))


setup(
    name='readfile',
    version=find_version('readfile/__init__.py'),
    description='A flexible module to read ascii files',
    author='Cristobal Sifon',
    author_email='sifon@astro.princeton.edu',
    long_description=read(os.path.join(_here, 'README.md')),
    url='https://github.com/cristobal-sifon/readfile',
    packages=['readfile'],
    install_requires=['numpy>=1.5.0'],
    zip_safe=False
    )
