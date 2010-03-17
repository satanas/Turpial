Turpial
=======

**Sumario:** Cliente Twitter escrito en Python. Ligero, funcional e integrado
al escritorio del usuario

*Turpial* es un cliente alternativo para la red *Twitter* con múltiples
interfaces. Está escrito en *Python* y tiene como meta ser una aplicación con
bajo consumo de recursos y que se integre al escritorio del usuario pero sin
renunciar a ninguna funcionalidad.

Actualmente *Turpial* se encuentra en estado de desarrollo, por lo que 
pueden presentarse errores y fallos inesperados. Es por esto que se invita a
los usuarios que detecten algún fallo lo reporten en la siguiente dirección: 

http://code.google.com/p/turpial/issues/list

*Turpial*, las imágenes y los sonidos han sido publicados bajo una licencia 
*GPL v3*. Vea el archivo ``COPYING`` para más detalles o visite 
http://www.gnu.org/licenses/gpl-3.0.html

Requisitos
----------

Turpial necesita los siguientes paquetes para funcionar correctamente:

 * ``python >= 2.5``
 * ``python-simplejson >= 1.9.2``
 * ``python-gtk2 >= 2.12``
 * ``python-notify >= 0.1.1``
 * ``python-pygame >= 1.7``
  
Una instalación estándar de *Python* (como la que viene en la mayoría de las
distribuciones GNU/Linux) es más que suficiente. El resto de los módulos se 
pueden instalar en las distribuciones basadas en Debian con el siguiente 
comando (como superusuario)::

    # aptitude install python-simplejson \
                       python-gtk2 \
                       python-notify \
                       python-pygame

o si dispone de ``sudo``::

    $ sudo aptitude install python-simplejson \
                            python-gtk2 \
                            python-notify \
                            python-pygame

Instalación
-----------

El proceso de instalación de la aplicación puede hacerlo de la siguiente
manera (como superusuario)::

    # python setup.py install

o si dispone de ``sudo``::

    $ sudo python setup.py install

Ejecutar
--------

Si desea ejecutar la aplicación solo debe escribir el comando ``turpial``::

    $ turpial [OPCIONES]

Por defecto, Turpial carga la interfaz ``gtk`` pero se pueden especificar los 
siguientes parámetros opcionales:

 * ``-d``: ejecuta Turpial en Modo Depuración 
 * ``-i interfaz``: para seleccionar la interfaz a cargar (``gtk`` | ``cmd``).

Si usted cumple con los requisitos para ejecutar *Turpial* pero no cuenta
con los permisos necesarios para instalarlo, puede ejecutar los siguientes
pasos desde el directorio ``Turpial``::

    $ export PYTHONPATH=$PWD
    $ python turpial/main.py [OPCIONES]

Para más información visita la página de Preguntas y Respuestas Frecuentes:

http://code.google.com/p/turpial/wiki/FAQ
