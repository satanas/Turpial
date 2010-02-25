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
      version="0.9.9-a1",
      description="Cliente Twitter escrito en Python",
      long_description=LONG_DESCRIPTION,
      author="Wil Alvarez",
      author_email="wil.alejandro@gmail.com",
      maintainer="Alexander Olivares",
      maintainer_email="olivaresa@gmail.com",
      url="http://code.google.com/p/turpial",
      download_url="http://code.google.com/p/turpial/downloads/list",
      license="GPLv3",
      scripts = ['turpial'],
      data_files = [
        ('/usr/share/turpial',['turpial.py']),
        ('/usr/share/turpial/core', glob.glob(os.path.join('core', '*.py'))),
        ('/usr/share/turpial/core/api', glob.glob(os.path.join('core', 'api', '*.py'))),
        ('/usr/share/turpial/core/api/poster', glob.glob(os.path.join('core', 'api', 'poster', '*.py'))),
        ('/usr/share/turpial/core/ui', glob.glob(os.path.join('core', 'ui', '*.py'))),
        ('/usr/share/turpial/core/ui/gtk_ui', glob.glob(os.path.join('core', 'ui', 'gtk_ui', '*.py'))),
        ('/usr/share/turpial/data/pixmaps', glob.glob(os.path.join('data', 'pixmaps', '*.png'))),
        ('/usr/share/turpial/data/sounds', glob.glob(os.path.join('data', 'sounds', '*.ogg'))),
        ('/usr/share/pixmaps', ['data/pixmaps/turpial_icon_48.png']),
        ('/usr/share/applications', ['turpial.desktop']),
        ('/usr/share/doc/turpial', ['doc/turpial.png', 
                       'doc/turpial.dia',
                       'bitacora',
                       'changelog',
                       'README',
                       'Canaima-Licencia',
                       'COPYING']),
      ],
      
      install_requires = ['python-simplejson >= 1.9.2', 
        'python-notify >= 0.1.1', 'python-pygame >= 1.7.0',],
)
