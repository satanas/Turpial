# -*- coding: utf-8 -*-

# Widgets para la ventana de preferencias del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import gtk

class Preferences(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.mainwin = parent
        self.set_default_size(360, 360)
        self.set_title('Preferences')
        self.set_border_width(6)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_close = gtk.Button(stock=gtk.STOCK_CLOSE)
        
        box_button = gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(gtk.BUTTONBOX_END)
        box_button.pack_start(btn_close)
        box_button.pack_start(btn_save)
        
        self.general = GeneralTab()
        
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(3)
        notebook.set_properties('tab-pos', gtk.POS_LEFT)
        notebook.append_page(self.general, gtk.Label('General'))
        
        vbox = gtk.VBox()
        #vbox.set_spacing(4)
        vbox.pack_start(notebook, True, True)
        vbox.pack_start(box_button, False, False)
        
        btn_close.connect('clicked', self.__close)
        btn_save.connect('clicked', self.__save)
        self.connect('delete-event', self.__close)
        
        self.add(vbox)
        self.show_all()
        
    def __close(self, widget, event=None):
        self.destroy()
        
    def __save(self, widget):
        return
        general = self.general.get_config()
        new_config = {'General': general}
        self.destroy()
        
        self.mainwin.request_save_config(new_config)
        
        
class TimeScroll(gtk.HBox):
    def __init__(self, label='', val=5, min=1, max=60, step=3, page=6, size=0,
        callback=None):
        gtk.HBox.__init__(self, False)
        
        self.callback = callback
        self.value = val
        lbl = gtk.Label(label)
        lbl.set_size_request(60, -1)
        adj = gtk.Adjustment(val, min, max, step, page, size)
        scale = gtk.HScale()
        scale.set_digits(0)
        scale.set_adjustment(adj)
        scale.set_property('value-pos', gtk.POS_RIGHT)
        
        self.pack_start(lbl, False, False, 3)
        self.pack_start(scale, True, True, 3)
        
        self.show_all()
        
        scale.connect('format-value', self.__format_value)
        scale.connect('value-changed', self.__on_change)
        
    def __format_value(self, widget, value):
        return "%s min" % value
        
    def __on_change(self, widget):
        self.value = widget.get_value()
        self.callback()
        
class GeneralTab(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False)
        
        description = gtk.Label('Ajusta cada cuanto tiempo quieres actualizar \
el timeline, las menciones y los mensajes directos')
        description.set_line_wrap(True)
        
        self.home = TimeScroll('Home', 3, callback=self.update_api_calls)
        self.replies = TimeScroll('Replies', 10, min=2, callback=self.update_api_calls)
        self.directs = TimeScroll('Directs', 15, min=5, callback=self.update_api_calls)
        
        self.estimated = gtk.Label(u'Usarás 0 llamadas a la API por hora')
        
        self.workspace = gtk.CheckButton('Wide Workspace')
        self.workspace.set_has_tooltip(True)
        self.workspace.set_tooltip_text('Muestra un espacio de trabajo de 3 columnas')
        
        self.profile_colors = gtk.CheckButton('Load profile color')
        self.profile_colors.set_has_tooltip(True)
        self.profile_colors.set_sensitive(False)
        self.profile_colors.set_tooltip_text('Utiliza los colores del perfil de \
usuario para resaltar menciones, hashtags y URLs')
        
        self.minimize = gtk.CheckButton('Minimize to tray on close')
        self.minimize.set_has_tooltip(True)
        self.minimize.set_tooltip_text('Envía a Turpial a la bandeja de sistema en \
lugar de cerrarla')

        self.remember = gtk.CheckButton('Remember login info')
        self.remember.set_has_tooltip(True)
        self.remember.set_sensitive(False)
        self.remember.set_tooltip_text('Recuerda la información de inicio de sesión')
        
        
        self.pack_start(description, False, False, 6)
        self.pack_start(self.home, False, False, 5)
        self.pack_start(self.replies, False, False, 5)
        self.pack_start(self.directs, False, False, 5)
        self.pack_start(self.estimated, False, False, 4)
        self.pack_start(self.workspace, False, False, 2)
        self.pack_start(self.profile_colors, False, False, 2)
        self.pack_start(self.minimize, False, False, 2)
        self.pack_start(self.remember, False, False, 2)
        self.show_all()
        self.update_api_calls()
        
    def update_api_calls(self):
        #print self.home.value
        #print self.replies.value
        #print self.directs.value
        calls = (60 / self.home.value) + (60 / self.replies.value) + (60 / self.directs.value)
        self.estimated.set_text(u'Usarás aprox. %i llamadas a la API por hora' % calls)
        
    def get_config(self):
        if self.workspace.get_active():
            workspace = 'wide'
        else:
            workspace = 'single'
        return {
            'home-update-interval': int(self.home.value),
            'replies-update-interval': int(self.replies.value),
            'directs-update-interval': int(self.directs.value),
            'workspace': workspace,
            #'main-win-geometry': self.cfg.get('General','main-win-geometry'),
        }
