from setuptools import setup
import os

setup_args = dict(
	name='snake-vs-block',
	version='0.0.1',
	description='snake vs block game',
	long_description='',
	author='adnu100',
	packages=['snakegame'],
	install_requires=['pysdl2'],
	include_package_data=True,
)

setup(**setup_args)
