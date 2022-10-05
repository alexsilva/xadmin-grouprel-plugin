# coding=utf-8
from setuptools import setup

setup(
    name='xadmin-group-related',
    version='3.2',
    packages=['xadmin_group_related',
              'xadmin_group_related.templatetags'],
    install_requires=["django-datatables-view"],
    url='https://github.com/alexsilva/xadmin-grouprel-plugin',
    license='MIT',
    author='alex',
    author_email='alex@fabricadigital.com.br',
    description='xadmin plugin that displays user related to a group (datatable)',
    include_package_data=True
)
