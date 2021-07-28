from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stocklab',
    version='0.6.0',
    description='A modular python programming interface to access financial '\
            'data from various sources.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hchsiao/stocklab',
    author='hchsiao',

    packages=find_packages(where='.'),
    python_requires='>=3.5',
    install_requires=[
        'pyDAL',
        'pyyaml',
        ],
)
