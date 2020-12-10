from __future__ import absolute_import, print_function

import os
import re
from setuptools import find_packages, setup

try:
    from myhelpers.setup_helpers import find_location, find_version, read
except ImportError as err:
    import sys
    print('{0}\nYou may download setup_helpers from'.format(err),
          'https://github.com/cristobal-sifon/myhelpers')
    sys.exit()


setup(
    name='readfile',
    version=find_version('src/readfile/__init__.py'),
    description='A flexible module to read ascii files',
    author='Cristobal Sifon',
    author_email='cristobal.sifon@pucv.cl',
    long_description=read(os.path.join(find_location(__file__), 'README.md')),
    url='https://github.com/cristobal-sifon/readfile',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['numpy>=1.5.0']
    )
