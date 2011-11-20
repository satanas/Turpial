#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.command.build import build as _build
from babel.messages import frontend as babel

LONG_DESCRIPTION = """
Turpial is a light, fast and beatiful microblogging client for GNU/Linux, 
written in Python and fully functional
"""

class build(_build):
    sub_commands = [('compile_catalog', None), ] + _build.sub_commands

    def run(self):
        """Run all sub-commands"""
        _build.run(self)

# TODO: Maybe find some better ways to do this
# looking distutils's copy_tree method
data_files=[
    ('./', ['AUTHORS']),
    ('share/pixmaps', ['turpial/data/pixmaps/turpial.png']),
    ('share/applications', ['turpial.desktop']),
    ('share/doc/turpial', ['ChangeLog',
                   'README.rst',
                   'COPYING']),
]
'''
pattern = re.compile('turpial/i18n/')
for root, dirs, files in os.walk(os.path.join('turpial', 'i18n')):
    for filename in files:
        if filename.endswith('.mo'):
            fullpath = os.path.join(root, filename)
            dest = os.path.join('/', 'usr', 'share', 'locale', re.sub(pattern, '', root))
            data_files.append((dest, [fullpath]))
'''
setup(name="turpial",
      version='2.0',
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
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Communications"
      ],
      packages=find_packages(),
      package_data={
        'turpial': ['data/pixmaps/*', 'data/sounds/*', 'data/themes/default/*']
      },
      entry_points={
        'console_scripts': [
            'turpial = turpial.main:Turpial',
        ],
      },
      cmdclass={
        'build': build,
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
      },
      data_files=data_files,
)
