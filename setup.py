from setuptools import setup

setup(name='readfile',
      version='1.0.1',
      description='A flexible module to read ascii files',
      author='Cristobal Sifon',
      author_email='sifon@strw.leidenuniv.nl',
      url='https://github.com/cristobal-sifon/readfile',
      modules=['readfile'],
      install_requires=['itertools',
                        'numpy>=1.5.0'])
