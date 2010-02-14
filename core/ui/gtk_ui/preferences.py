# -*- coding: utf-8 -*-

# Widgets para la ventana de preferencias del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import gtk

from core.api import *

class Preferences(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.mainwin = parent
        self.current = parent.read_config()
        self.set_default_size(360, 380)
        self.set_title('Preferencias')
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
        
        # Tabs
        self.general = GeneralTab(self.current['General'])
        self.notif = NotificationsTab(self.current['Notifications'])
        self.services = ServicesTab(self.current['Services'])
        self.muted = MutedTab(self.mainwin)
        
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(3)
        notebook.set_properties('tab-pos', gtk.POS_LEFT)
        notebook.append_page(self.general, gtk.Label('General'))
        notebook.append_page(self.notif, gtk.Label('Notificaciones'))
        notebook.append_page(self.services, gtk.Label('Servicios'))
        notebook.append_page(self.muted, gtk.Label('Silenciar'))
        
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
        general = self.general.get_config()
        notif = self.notif.get_config()
        services = self.services.get_config()
        
        new_config = {
            'General': general, 
            'Notifications': notif, 
            'Services': services
        }
        self.destroy()
        
        self.mainwin.save_config(new_config)
        self.mainwin.request_update_muted(self.muted.get_muted())
        
        
class PreferencesTab(gtk.VBox):
    def __init__(self, desc, current=None):
        gtk.VBox.__init__(self, False)
        
        self.current = current
        description = gtk.Label()
        description.set_line_wrap(True)
        description.set_use_markup(True)
        description.set_markup(desc)
        description.set_justify(gtk.JUSTIFY_FILL)
        #desc_box = gtk.HBox(False, 3)
        #desc_box.pack_start(description, True, True)
        
        desc_align = gtk.Alignment(xalign=0.0, yalign=0.0)
        desc_align.set_padding(0, 5, 10, 10)
        desc_align.add(description)
        
        self.pack_start(desc_align, False, False, 5)
        
    def get_config(self):
        raise NotImplemented
        
class TimeScroll(gtk.HBox):
    def __init__(self, label='', val=5, min=1, max=60, step=3, page=6, size=0,
        callback=None, lbl_size=70, unit='min'):
        gtk.HBox.__init__(self, False)
        
        self.callback = callback
        self.value = val
        self.unit = unit
        lbl = gtk.Label(label)
        lbl.set_size_request(lbl_size, -1)
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
        return "%i %s" % (int(value), self.unit)
        
    def __on_change(self, widget):
        self.value = widget.get_value()
        if self.callback: self.callback()
        
class GeneralTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, 'Ajusta cada cuanto tiempo quieres \
actualizar el timeline, las menciones y los mensajes directos', current)
        
        h = int(self.current['home-update-interval'])
        r = int(self.current['replies-update-interval'])
        d = int(self.current['directs-update-interval'])
        t = int(self.current['num-tweets'])
        pf = True if self.current['profile-color'] == 'on' else False
        ws = True if self.current['workspace'] == 'wide' else False
        min = True if self.current['minimize-on-close'] == 'on' else False
        
        self.home = TimeScroll('Timeline', h, callback=self.update_api_calls)
        self.replies = TimeScroll('Menciones', r, min=2, callback=self.update_api_calls)
        self.directs = TimeScroll('Directos', d, min=5, callback=self.update_api_calls)
        
        self.tweets = TimeScroll('Tweets mostrados', t, min=20, max=200, unit='', lbl_size=120)
        
        self.estimated = gtk.Label(u'Usarás 0 llamadas a la API por hora')
        est_align = gtk.Alignment(xalign=0.5)
        est_align.set_padding(0, 8, 0, 0)
        est_align.add(self.estimated)
        
        self.workspace = gtk.CheckButton('Modo extendido')
        self.workspace.set_active(ws)
        try:
            self.workspace.set_has_tooltip(True)
            self.workspace.set_tooltip_text('Muestra un espacio de trabajo de 3 columnas')
        except:
            pass
        
        self.profile_colors = gtk.CheckButton('Cargar color de perfil (Requiere reiniciar)')
        self.profile_colors.set_active(pf)
        try:
            self.profile_colors.set_has_tooltip(True)
            self.profile_colors.set_tooltip_text('Utiliza los colores del \
perfil de usuario para resaltar menciones, hashtags y URLs')
        except:
            pass
        
        self.minimize = gtk.CheckButton('Minimizar a la bandeja')
        self.minimize.set_active(min)
        try:
            self.minimize.set_has_tooltip(True)
            self.minimize.set_tooltip_text('Envía a Turpial a la bandeja de \
sistema en lugar de cerrarlo')
        except:
            pass

        self.remember = gtk.CheckButton(u'Recordar info de sesión')
        self.remember.set_sensitive(False)
        try:
            self.remember.set_has_tooltip(True)
            self.remember.set_tooltip_text('Recuerda la información de inicio de sesión')
        except:
            pass
        
        
        self.pack_start(self.home, False, False, 5)
        self.pack_start(self.replies, False, False, 5)
        self.pack_start(self.directs, False, False, 5)
        self.pack_start(est_align, False, False, 4)
        self.pack_start(self.tweets, False, False, 10)
        self.pack_start(self.workspace, False, False, 2)
        self.pack_start(self.profile_colors, False, False, 2)
        self.pack_start(self.minimize, False, False, 2)
        self.pack_start(self.remember, False, False, 2)
        self.show_all()
        self.update_api_calls()
        
    def update_api_calls(self):
        calls = (60 / self.home.value) + (60 / self.replies.value) + (60 / self.directs.value)
        self.estimated.set_text(u'Usarás aprox. %i llamadas a la API por hora' % calls)
        
    def get_config(self):
        ws = 'wide' if self.workspace.get_active() else 'single'
        min = 'on' if self.minimize.get_active() else 'off'
        pf = 'on' if self.profile_colors.get_active() else 'off'
        
        return {
            'home-update-interval': int(self.home.value),
            'replies-update-interval': int(self.replies.value),
            'directs-update-interval': int(self.directs.value),
            'workspace': ws,
            'profile-color': pf,
            'minimize-on-close': min,
            'num-tweets': int(self.tweets.value),
        }

class NotificationsTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, 'Selecciona las notificaciones que \
deseas recibir de Turpial', current)
        
        home = True if self.current['home'] == 'on' else False
        replies = True if self.current['replies'] == 'on' else False
        directs = True if self.current['directs'] == 'on' else False
        login = True if self.current['login'] == 'on' else False
        sound = True if self.current['sound'] == 'on' else False
        
        self.timeline = gtk.CheckButton('Timeline')
        self.timeline.set_active(home)
        try:
            self.timeline.set_has_tooltip(True)
            self.timeline.set_tooltip_text('Muestra una notificación cada vez \
que se actualiza el timeline')
        except:
            pass
            
        self.replies = gtk.CheckButton('Menciones')
        self.replies.set_active(replies)
        try:
            self.replies.set_has_tooltip(True)
            self.replies.set_tooltip_text('Muestra una notificación cuando se \
reciben menciones de otros usuarios')
        except:
            pass
            
        self.directs = gtk.CheckButton('Mensajes Directos')
        self.directs.set_active(directs)
        try:
            self.directs.set_has_tooltip(True)
            self.directs.set_tooltip_text(u'Muestra una notificación cuando se \
reciben mensajes directos')
        except:
            pass
            
        self.profile = gtk.CheckButton('Inicio')
        self.profile.set_active(login)
        try:
            self.profile.set_has_tooltip(True)
            self.profile.set_tooltip_text(u'Muestra una notificación al inicio \
de la sesión con información del perfil de usuario')
        except:
            pass
        
        self.sounds = gtk.CheckButton('Activar sonidos')
        self.sounds.set_active(sound)
        try:
            self.sounds.set_has_tooltip(True)
            self.sounds.set_tooltip_text(u'Activa los sonidos con cada \
notificación')
        except:
            pass
            
        self.pack_start(self.timeline, False, False, 2)
        self.pack_start(self.replies, False, False, 2)
        self.pack_start(self.directs, False, False, 2)
        self.pack_start(self.profile, False, False, 2)
        self.pack_start(self.sounds, False, False, 6)
        self.show_all()
        
    def get_config(self):
        home = 'on' if self.timeline.get_active() else 'off'
        replies = 'on' if self.replies.get_active() else 'off'
        directs = 'on' if self.directs.get_active() else 'off'
        profile = 'on' if self.profile.get_active() else 'off'
        sound = 'on' if self.sounds.get_active() else 'off'
        
        return {
            'home': home,
            'replies': replies,
            'directs': directs,
            'login': profile,
            'sound': sound,
        }
        
class ServicesTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, u'Selecciona los servicios que deseas \
usar para cortar URLs y subir imágenes a Twitter', current)
        i = 0
        default = -1
        url_lbl = gtk.Label('Cortar URL')
        self.shorten = gtk.combo_box_new_text()
        for key,v in URL_SERVICES.iteritems():
            self.shorten.append_text(key)
            if key == self.current['shorten-url']: default = i
            i += 1
        self.shorten.set_active(default)
        
        url_box = gtk.HBox(False)
        url_box.pack_start(url_lbl, False, False, 3)
        url_box.pack_start(self.shorten, False, False, 3)
        
        pic_lbl = gtk.Label(u'Subir imágenes')
        self.upload = gtk.combo_box_new_text()
        for key in PHOTO_SERVICES:
            self.upload.append_text(key)
            if key == self.current['upload-pic']: default = i
            i += 1
        self.upload.set_active(default)
        
        pic_box = gtk.HBox(False)
        pic_box.pack_start(pic_lbl, False, False, 3)
        pic_box.pack_start(self.upload, False, False, 3)
        
        self.pack_start(url_box, False, False, 2)
        self.pack_start(pic_box, False, False, 2)
        self.show_all()
        
    def get_config(self):
        return {
            'shorten-url': self.shorten.get_active_text(),
            'upload-pic': self.upload.get_active_text(),
        }
        
class MutedTab(PreferencesTab):
    def __init__(self, parent):
        PreferencesTab.__init__(self, u'Selecciona los usuarios que deseas \
silenciar temporalmente')
        
        self.muted = []
        self.mainwin = parent
        self.friends, self.muted = self.mainwin.request_muted_list()
        
        self.model = gtk.ListStore(str, bool)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.list.set_model(self.model)
        
        cell_check = gtk.CellRendererToggle()
        cell_check.set_property('activatable', True)
        cell_user = gtk.CellRendererText()
        
        column = gtk.TreeViewColumn('')
        column.set_alignment(0.0)
        column.pack_start(cell_check, False)
        column.pack_start(cell_user, True)
        column.set_attributes(cell_check, active=1)
        column.set_attributes(cell_user, markup=0)
        self.list.append_column(column)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)
        
        cell_check.connect("toggled", self.__toggled)
        
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_markup(u'<span foreground="#920d12">Aún no he terminado \
de cargar todos los contactos. Intententa de nuevo en unos segundos</span>')
        label.set_justify(gtk.JUSTIFY_FILL)
        
        align = gtk.Alignment(xalign=0.0, yalign=0.0)
        align.set_padding(0, 5, 10, 10)
        align.add(label)
        
        if self.friends:
            for f in self.friends:
                mark = True if (f in self.muted) else False
                self.model.append([f, mark])
                
            self.pack_start(scroll, True, True, 2)
        else:
            self.pack_start(align, True, True, 2)
        
        self.show_all()
        
    def __process(self, model, path, iter):
        user = model.get_value(iter, 0)
        mark = model.get_value(iter, 1)
        
        if mark:
            self.muted.append(user)
            
    def __toggled(self, widget, path):
        value = not self.model[path][1]
        self.model[path][1] = value
        
    def get_muted(self):
        self.muted = []
        self.model.foreach(self.__process)
        return self.muted
