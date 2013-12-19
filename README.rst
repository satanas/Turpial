Turpial
=======

**Summary:** Turpial is a light, fast and beautiful microblogging client 
written in Python

*Turpial* is an alternative client for microblogging with multiple interfaces.
At the moment it supports Twitter and Identi.ca and works with Gtk and Qt 
interfaces, but we are still working on more fancy features.

Currently  *Turpial* is in heavy development, so probably you will find bugs or 
undesired behavior. In this cases please report issues at:

http://dev.turpial.org.ve/projects/turpial/issues

We will be very graceful for your contributions.


License
-------

*Turpial* source code, images and sounds have been released under the *GPL v3* 
License. Please check the ``COPYING`` file for more details or visit 
http://www.gnu.org/licenses/gpl-3.0.html


Requirements
------------

Turpial needs this packages to work properly:

 * ``python >= 2.5``
 * ``libturpial >= 0.8.x``
 * ``notify >= 0.1.1`` (python-notify)
 * ``gst0.10`` (gstreamer0.10-python)
 * ``pybabel >= 0.9.1`` (python-babel)
 * ``webkit``  (pywebkitgtk)
 * ``setuptools`` (python2-distribute)
 * ``pkg-resources``

Currently Turpial suports 3 different interfaces: Shell, Gtk and Qt. The shell 
interface needs no more dependencies to work, but if you are planning to run 
Gtk or Qt you will need to install a couple of more dependencies:

For Gtk:

 * ``gtk2 >= 2.12`` (python-gtk2)
 * ``gtkspell >= 2.25.3`` (python2-gtkspell)

For Qt:

 * ``pyqt4 >= 2.12`` (python-pyqt4)


Installation
------------

Turpial is available on most popular Linux distributions, so you should be able 
to install it using your favorite package manager (aptitude, apt-get, pacman,
yum). Please visit http://turpial.org.ve/downloads for more information.

To install Turpial from sources you should go to source folder and 
run (as superuser)::

    # python setup.py install

or using ``sudo``::

    $ sudo python setup.py install


Usage
-----

After installation just execute ``turpial`` in a shell::

    $ turpial [OPTIONS]

Turpial will try to identify your desktop environment and load the interface 
that best suit to it. If you use a Gtk based environment then Turpial will 
load Gtk interface but in a non-Gtk based environment it will load the Qt 
interface. However you can override this behavior using optional parameters:

 * ``-i interface``: You can choose between ``gtk`` and ``cmd``.
 * ``-d``: runs Turpial in Debugging Mode.


Further Information
-------------------

For more information visit our FAQ page http://turpial.org.ve/faqs/


Contact
-------

You can follow Turpial news from our official Twitter account:

 * @TurpialVe

Join to the official development mailing list:

http://groups.google.com/group/turpial-dev

Or mail us to say what an awesome/crappy app Turpial is. Our contact info is
in:

http://turpial.org.ve/team


Donate
------

You love Turpial and want to show us how gracefull you are? Buy us a coffee :)

PayPal donations at:

https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XUNXXJURA7FLW

Flattr:

http://flattr.com/thing/452623/Turpial

