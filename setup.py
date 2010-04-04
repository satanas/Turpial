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
      packages=find_packages(),
      package_data={
        'turpial': ['data/pixmaps/*', 'data/sounds/*', 'data/themes/default/*',
                    'i18n/*.*', 'i18n/*/LC_MESSAGES/*.*']
      },
      entry_points={
        'console_scripts': [
            'turpial = turpial.main:Turpial',
        ],
      },
      cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
      },
      data_files=[
        ('share/pixmaps', ['turpial/data/pixmaps/turpial_icon_48.png']),
        ('share/applications', ['turpial.desktop']),
        ('share/doc/turpial', ['doc/turpial.png',
                       'doc/turpial.dia',
                       'ChangeLog',
                       'README.rst',
                       'COPYING']),
      ],
)
