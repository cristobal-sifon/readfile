from __future__ import absolute_import, print_function

import os
import re
from setuptools import setup

try:
    from myhelpers.setup_helpers import find_location, find_version, read
except ImportError as err:
    import sys
    print('{0}\nYou may download setup_helpers from'.format(err),
          'https://github.com/cristobal-sifon/myhelpers')
    sys.exit()


setup(
    name='readfile',
    version=find_version('readfile/__init__.py'),
    description='A flexible module to read ascii files',
    author='Cristobal Sifon',
    author_email='sifon@astro.princeton.edu',
    long_description=read(os.path.join(find_location(__file__), 'README.md')),
    url='https://github.com/cristobal-sifon/readfile',
    packages=['readfile'],
    install_requires=['numpy>=1.5.0'],
    zip_safe=False
    )
