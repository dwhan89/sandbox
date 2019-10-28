#-
# setup.py
#-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = dict(description='random set up code snippets that I play with', author="Dongwon 'DW' HAN",
              url='https://github.com/dwhan89/sandbox', download_url='https://github.com/dwhan89/sandbox',
              author_email='dongwon.han@stonybrook.edu', version='1.1.1', install_requires=[
        'numpy',
        'matplotlib'
    ], packages=[
        'sandbox'
    ], scripts=[], name='sandbox')

setup(**config)
