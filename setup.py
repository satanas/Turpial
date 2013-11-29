#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from babel.messages import frontend as babel
from distutils.command.build import build as _build

from turpial import VERSION

LONG_DESCRIPTION = """
Turpial is a light, fast and beautiful microblogging client written in Python
"""

class build(_build):

    def get_sub_commands(self):
        sub_commands = _build.get_sub_commands(self)
        print sub_commands
        return [('compile_catalog', None), ] + sub_commands

# TODO: Maybe find some better ways to do this
# looking distutils's copy_tree method
data_files=[
    ('share/icons/scalable/apps', ['turpial/data/pixmaps/turpial.svg']),
    ('share/pixmaps', ['turpial/data/pixmaps/turpial.png']),
    ('share/applications', ['turpial.desktop']),
    ('share/doc/turpial', ['ChangeLog', 'README.rst', 'AUTHORS', 'COPYING', 'TRANSLATORS', 'THANKS']),
]

setup(name="turpial",
    version=VERSION,
    description="A light, beautiful and functional microblogging client",
    long_description=LONG_DESCRIPTION,
    author="Wil Alvarez",
    author_email="wil.alejandro@gmail.com",
    maintainer="Wil Alvarez",
    maintainer_email="wil.alejandro@gmail.com",
    url="http://turpial.org.ve",
    download_url="http://turpial.org.ve/downloads",
    license="GPLv3",
    keywords='twitter identi.ca microblogging turpial',
    classifiers=[
      "Development Status :: 4 - Beta",
      "Environment :: X11 Applications :: GTK",
      "Intended Audience :: End Users/Desktop",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Operating System :: POSIX :: Linux",
      "Programming Language :: Python",
      "Topic :: Communications"
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={
      'turpial': ['data/pixmaps/*', 'data/sounds/*', 'data/fonts/*', 'turpial/ui/qt/*',
          'turpial/i18n/*', 'turpial/ui/qt/templates/*'],
    },
    entry_points={
      'console_scripts': [
          'turpial = turpial.main:main',
          #'turpial-unity-daemon = turpial.ui.unity.daemon:main',
      ],
    },
    cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
    },
    data_files=data_files,
)
