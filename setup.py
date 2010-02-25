#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

LONG_DESCRIPTION="""
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
      version="0.9.3",
      description="Cliente Twitter escrito en Python",
      long_description=LONG_DESCRIPTION,
      author="Wil Alvarez",
      author_email="wil.alejandro@gmail.com",
      maintainer="Milton Mazzarri",
      maintainer_email="milmazz@gmail.com",
      url="http://code.google.com/p/turpial",
      download_url="http://code.google.com/p/turpial/downloads/list",
      license="GPLv3",
      packages=['turpial', 'core.api', 'core.ui', 'core.ui.gtk_ui'],
      entry_points={
        'console_scripts': [
            'turpial = Turpial',
        ],
      },
      data_files = [
        ('data/pixmaps', glob.glob(os.path.join('data', 'pixmaps', '*.png'))),
        ('data/sounds', glob.glob(os.path.join('data', 'sounds', '*.wav'))),
        ('/usr/share/pixmaps', ['data/pixmaps/turpial_icon_48.png']),
        ('/usr/share/applications', ['turpial.desktop']),
        ('share/doc', ['doc/turpial.png', 
                       'doc/turpial.dia',
                       'bitacora',
                       'changelog',
                       'README',
                       'COPYING']),
      ],
      
      install_requires = ['python-simplejson >= 1.9.2', 
        'python-notify >= 0.1.1', 'python-pygame >= 1.7.0',],
)
