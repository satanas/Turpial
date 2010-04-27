=========================================================================================
:mod:`config` -- Módulo para manejar los archivos de configuración de usuario del Turpial
=========================================================================================

.. currentmodule:: turpial.config

.. autoclass:: ConfigBase()

:class:`ConfigBase` methods
---------------------------

.. automethod:: ConfigBase.__init__
.. automethod:: ConfigBase.create
.. automethod:: ConfigBase.load
.. automethod:: ConfigBase.save
.. automethod:: ConfigBase.write
.. automethod:: ConfigBase.write_section
.. automethod:: ConfigBase.read
.. automethod:: ConfigBase.read_section
.. automethod:: ConfigBase.read_all

.. autoclass:: ConfigHandler(ConfigBase)

:class:`ConfigHandler` methods
------------------------------

.. automethod:: ConfigHandler.__init__
.. automethod:: ConfigHandler.create_muted_list
.. automethod:: ConfigHandler.load_muted_list
.. automethod:: ConfigHandler.save_muted_list

.. autoclass:: ConfigApp(ConfigBase)

:class:`ConfigApp` methods
--------------------------

.. automethod:: ConfigApp.__init__
