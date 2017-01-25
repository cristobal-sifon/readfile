import re
from setuptools import setup


#Taken from the Python docs:
#Utility function to read the README file.
#Used for the long_description.  It's nice, because now 1) we have a
#top level README file and 2) it's easier to type in the README file
#than to put a raw string in below
def read(fname):
    return open(os.path.join(here, fname)).read()


#this function copied from pip's setup.py
#https://github.com/pypa/pip/blob/1.5.6/setup.py
#so that the version is only set in the __init__.py and then read here
#to be consistent
def find_version(fname):
    version_file = read(fname)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='readfile',
      version=find_version('__init__.py'),
      description='A flexible module to read ascii files',
      author='Cristobal Sifon',
      author_email='sifon@astro.princeton.edu',
      url='https://github.com/cristobal-sifon/readfile',
      modules=['readfile'],
      install_requires=['numpy>=1.5.0'])
