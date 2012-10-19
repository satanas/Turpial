# -*- coding: utf-8 -*-

""" Preferences window for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk

from turpial.ui.lang import i18n
from turpial.ui.gtk.preferences.tabs import *

class PreferencesDialog(Gtk.Window):
    def __init__(self, parent=None, mode='user'):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.mainwin = parent
        self.current = parent.get_config()
        self.set_default_size(450, 400)
        self.set_title(i18n.get('preferences'))
        self.set_border_width(6)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        btn_save = Gtk.Button(i18n.get('save'))
        btn_close = Gtk.Button(i18n.get('close'))

        box_button = Gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(Gtk.ButtonBoxStyle.END)
        box_button.pack_start(btn_close, False, False, 0)
        box_button.pack_start(btn_save, False, False, 0)

        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(3)
        notebook.set_properties('tab-pos', Gtk.PositionType.LEFT)

        # Tabs
        self.general = GeneralTab(self.current['General'])
        self.notif = NotificationsTab(self.current['Notifications'], self.current['Sounds'])
        self.services = ServicesTab(self.current['Services'])
        self.browser = BrowserTab(self.mainwin, self.current['Browser'])
        self.filtered = FilterTab(self.mainwin)
        #self.proxy = ProxyTab(self.current['Proxy'])
        self.advanced = AdvancedTab(self.mainwin, self.current['Advanced'])

        notebook.append_page(self.general, Gtk.Label(i18n.get('general')))
        notebook.append_page(self.notif, Gtk.Label(i18n.get('notifications')))
        notebook.append_page(self.services, Gtk.Label(i18n.get('services')))
        notebook.append_page(self.browser, Gtk.Label(i18n.get('web_browser')))
        notebook.append_page(self.filtered, Gtk.Label(i18n.get('filters')))
        #notebook.append_page(self.proxy, Gtk.Label(i18n.get('proxy')))
        notebook.append_page(self.advanced, Gtk.Label(i18n.get('advanced')))

        vbox = Gtk.VBox()
        #vbox.set_spacing(4)
        vbox.pack_start(notebook, True, True, 0)
        vbox.pack_start(box_button, False, False, 0)

        btn_close.connect('clicked', self.__close)
        btn_save.connect('clicked', self.__save)
        self.connect('delete-event', self.__close)

        self.add(vbox)

        self.showed = False

    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

    def show(self):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.show_all()

    def quit(self):
        self.destroy()

    def __save(self, widget):
        general = self.general.get_config()
        notif, sounds = self.notif.get_config()
        services = self.services.get_config()
        browser = self.browser.get_config()
        proxy = self.proxy.get_config()
        advanced = self.advanced.get_config()

        new_config = {
            'General': general,
            'Notifications': notif,
            'Sounds': sounds,
            'Services': services,
            'Browser': browser,
            'Proxy': proxy,
            'Advanced': advanced,
        }

        self.mainwin.save_config(new_config)
        self.mainwin.save_filters(self.filtered.get_filters())
        self.destroy()

