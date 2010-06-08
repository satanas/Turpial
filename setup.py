#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.command.build import build as _build
from babel.messages import frontend as babel
from turpial.config import GLOBAL_CFG

LONG_DESCRIPTION = """
Este proyecto intenta ser un cliente alternativo para la red Twitter
con múltiples interfaces. Está escrito en Python y tiene como meta ser
una aplicación con bajo consumo de recursos y que se integre al
escritorio del usuario pero sin renunciar a ninguna funcionalidad.

No son solo ganas de reinventar la rueda (considerando que
DestroyTwitter, TweetDeck et al. están disponibles para Linux), sino
que se quiere lograr un cliente que se integre mejor con el escritorio
Linux y que corra en entornos de escritorio ligeros como Fluxbox,
OpenBox, etc (pensando en las netbooks), ya que Adobe Air, por ejemplo,
solo corre en KDE/GNOME y la mayoría de los clientes GTK carecen de una
gran cantidad de funciones.

Está inspirado por la interfaz y funcionalidad de DestroyTwitter pero
emplea diferentes recursos y tecnologías como Cairo y Webkit.
"""

class build(_build):
    sub_commands = [('compile_catalog', None), ] + _build.sub_commands

    def run(self):
        """Run all sub-commands"""
        _build.run(self)

setup(name="turpial",
      version=GLOBAL_CFG['App']['version'],
      description="Cliente Twitter escrito en Python",
      long_description=LONG_DESCRIPTION,
      author="Wil Alvarez",
      author_email="wil.alejandro@gmail.com",
      maintainer="Milton Mazzarri",
      maintainer_email="milmazz@gmail.com",
      url="http://code.google.com/p/turpial",
      download_url="http://code.google.com/p/turpial/downloads/list",
      license="GPLv3",
      keywords='twitter turpial oauth',
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
      data_files=[
        ('share/pixmaps', ['turpial/data/pixmaps/turpial.png']),
        ('share/applications', ['turpial.desktop']),
        ('share/doc/turpial', ['doc/turpial.png',
                       'doc/turpial.dia',
                       'ChangeLog',
                       'README.rst',
                       'COPYING']),
      ],
)
