# This script is for dataflow to install any pipeline dependencies needed but can also
# serve as an easy way to install packages for our local environments too by simply running
# pip install .
# in the command line

import setuptools

name = 'crypto-trading-v2'
version = '0.0.1'

setuptools.setup(
    name=name,
    version=version,
    install_requires=[
        'apache-beam[gcp]==2.43.0',
        'requests==2.28.1',
    ],
    packages=setuptools.find_packages(),
)
