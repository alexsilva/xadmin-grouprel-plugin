from setuptools import setup

setup(
    name='xadmin-grouprel-plugin',
    version='2.0',
    packages=['xplugin_grouprel',
              'xplugin_grouprel.templatetags'],
    install_requires=["django-datatables-view"],
    url='https://github.com/alexsilva/xadmin-grouprel-plugin',
    license='MIT',
    author='alex',
    author_email='alex@fabricadigital.com.br',
    description='xadmin plugin that displays user related to a group (datatable)',
    include_package_data=True
)
