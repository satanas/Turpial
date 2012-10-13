# -*- coding: utf-8 -*-

""" Preferences tabs for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)

import subprocess


from turpial.ui.lang import i18n
from turpial.ui.gtk.preferences.widgets import *

from libturpial.api.services.shorturl import URL_SERVICES
from libturpial.api.services.uploadpic import PIC_SERVICES

class GeneralTab(GenericTab):
    def __init__(self, current):
        GenericTab.__init__(
            self,
            _('Adjust update frequency for columns'),
            current
        )

        interval = int(self.current['update-interval'])
        tweets = int(self.current['statuses'])
        profile = True if self.current['profile-color'] == 'on' else False
        minimize = True if self.current['minimize-on-close'] == 'on' else False

        self.interval = TimeScroll(_('Update Interval'), interval, unit='min')
        self.tweets = TimeScroll(_('Statuses'), tweets, min=20, max=200)

        self.profile_colors = CheckBox(_('Load profile color'), profile,
            _('Use your profile color for highlighted elements'))
        self.profile_colors.set_sensitive(False)

        self.minimize = CheckBox(_('Minimize to tray'), minimize,
            _('Send Turpial to system tray when closing main window'))

        self.add_child(self.interval, False, False, 5)
        self.add_child(self.tweets, False, False, 5)
        self.add_child(HSeparator(), False, False)
        self.add_child(self.profile_colors, False, False, 2)
        self.add_child(self.minimize, False, False, 2)
        self.show_all()

    def get_config(self):
        minimize = 'on' if self.minimize.get_active() else 'off'
        profile = 'on' if self.profile_colors.get_active() else 'off'

        return {
            'update-interval': int(self.interval.value),
            'profile-color': profile,
            'minimize-on-close': minimize,
            'statuses': int(self.tweets.value),
        }

class NotificationsTab(GenericTab):
    def __init__(self, notif, sounds):
        GenericTab.__init__(
            self,
            _('Select the notifications you want to receive from Turpial'),
            None
        )
        self.notif = notif
        self.sounds = sounds

        nupdates  = True if self.notif['updates'] == 'on' else False
        nlogin = True if self.notif['login'] == 'on' else False
        nicon = True if self.notif['icon'] == 'on' else False
        slogin = True if self.sounds['login'] == 'on' else False
        supdates = True if self.sounds['updates'] == 'on' else False

        self.nupdates = CheckBox(_('Updates'), nupdates,
            _('Show a notification when you get updates'), 10)

        self.nlogin = CheckBox(_('Login'), nlogin,
            _('Show a notification at login with user profile'), 10)

        self.nicon = CheckBox(_('Tray icon'), nicon, 
            _('Change the tray icon when you have notifications'), 10)

        self.slogin = CheckBox(_('Login'), slogin,
            _('Play a sound when you login'), 10)

        self.supdates = CheckBox(_('Updates'), supdates,
            _('Play a sound when you get updates'), 10)

        self.add_child(TitleLabel(_('Notifications')), False, False)
        self.add_child(self.nlogin, False, False, 2)
        self.add_child(self.nupdates, False, False, 2)
        self.add_child(self.nicon, False, False, 2)
        self.add_child(TitleLabel(_('Sounds')), False, False)
        self.add_child(self.slogin, False, False, 2)
        self.add_child(self.supdates, False, False, 2)
        self.show_all()

    def get_config(self):
        nupdates = 'on' if self.nupdates.get_active() else 'off'
        nlogin = 'on' if self.nlogin.get_active() else 'off'
        nicon = 'on' if self.nicon.get_active() else 'off'
        slogin = 'on' if self.slogin.get_active() else 'off'
        supdates = 'on' if self.supdates.get_active() else 'off'

        return {
            'updates': nupdates,
            'login': nlogin,
            'icon': nicon,
        }, {
            'login': slogin,
            'updates': supdates,
        }

class ServicesTab(GenericTab):
    def __init__(self, current):
        GenericTab.__init__(
            self,
            _('Select your preferred services to shorten URLs and to upload images'),
            current
        )

        self.shorten = ComboBox(_('Shorten URL'), URL_SERVICES, self.current['shorten-url'])
        self.upload = ComboBox(_('Upload images'), PIC_SERVICES, self.current['upload-pic'])

        self.add_child(self.shorten, False, False, 2)
        self.add_child(self.upload, False, False, 2)
        self.show_all()

    def get_config(self):
        return {
            'shorten-url': self.shorten.get_active_text(),
            'upload-pic': self.upload.get_active_text(),
        }

class FilterTab(GenericTab):
    def __init__(self, parent):
        GenericTab.__init__(
            self, 
            _("Filter out anything that bothers you")
        )

        self.mainwin = parent

        self.filtered = self.mainwin.get_filters()
        self.updated_filtered = set(self.filtered)

        self.term_input = Gtk.Entry()
        self.term_input.connect('activate', self.__add_filter)

        add_button = Gtk.Button(stock=Gtk.STOCK_ADD)
        add_button.set_size_request(80, -1)
        add_button.connect("clicked", self.__add_filter)
        self.del_button = Gtk.Button(stock=Gtk.STOCK_DELETE)
        self.del_button.set_size_request(80, -1)
        self.del_button.set_sensitive(False)
        self.del_button.connect("clicked", self.__remove_filter)

        input_box = Gtk.HBox()
        input_box.pack_start(self.term_input, True, True, 2)
        input_box.pack_start(add_button, False, False, 0)
        input_box.pack_start(self.del_button, False, False, 0)

        self.model = Gtk.ListStore(str)
        self._list = Gtk.TreeView()
        self._list.set_headers_visible(False)
        self._list.set_level_indentation(0)
        self._list.set_rules_hint(True)
        self._list.set_resize_mode(Gtk.ResizeMode.IMMEDIATE)
        self._list.set_model(self.model)
        self._list.connect('cursor-changed', self.__cursor_changed)

        column = Gtk.TreeViewColumn('')
        column.set_alignment(0.0)
        term = Gtk.CellRendererText()
        column.pack_start(term, True)
        column.add_attribute(term, 'markup', 0)
        self._list.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self._list)

        for filtered_item in self.filtered:
            self.model.append([filtered_item])

        self.add_child(input_box, False, False, 2)
        self.add_child(scroll, True, True, 2)
        self.show_all()

    def __process(self, model, path, iter):
        filtered_item = model.get_value(iter, 0)
        self.filtered.append(filtered_item)

    def __cursor_changed(self, widget):
        self.del_button.set_sensitive(True)

    def __add_filter(self, widget):
        new_filter = self.term_input.get_text()
        if (new_filter != '') and (new_filter not in self.updated_filtered):
            self.model.append([new_filter])
            self.updated_filtered.add(new_filter)
        self.term_input.set_text("")
        self.term_input.grab_focus()

    def __remove_filter(self, widget):
        model, term = self._list.get_selection().get_selected()
        if term:
            str_term = self.model.get_value(term, 0)
            self.model.remove(term)
            self.updated_filtered.remove(str_term)
            self.del_button.set_sensitive(False)
            self.term_input.grab_focus()

    def get_filters(self):
        self.filtered = []
        self.model.foreach(self.__process)
        return self.filtered

class BrowserTab(GenericTab):
    def __init__(self, parent, current):
        GenericTab.__init__(
            self,
            _('Setup your favorite web browser to open all links'),
            current
        )

        self.mainwin = parent

        chk_default = Gtk.RadioButton.new_with_label_from_widget(None, _('Default web browser'))
        chk_other = Gtk.RadioButton.new_with_label_from_widget(chk_default, _('Choose another web browser'))

        cmd_lbl = Gtk.Label(_('Command'))
        cmd_lbl.set_size_request(90, -1)
        cmd_lbl.set_alignment(1.0, 0.5)
        self.command = Gtk.Entry()
        btn_test = Gtk.Button(_('Test'))
        btn_browse = Gtk.Button(_('Browse'))

        cmd_box = Gtk.HBox(False)
        cmd_box.pack_start(cmd_lbl, False, False, 3)
        cmd_box.pack_start(self.command, True, True, 3)

        buttons_box = Gtk.HButtonBox()
        buttons_box.set_spacing(6)
        buttons_box.set_layout(Gtk.ButtonBoxStyle.END)
        buttons_box.pack_start(btn_test, False, False, 0)
        buttons_box.pack_start(btn_browse, False, False, 0)

        self.other_vbox = Gtk.VBox(False, 2)
        self.other_vbox.pack_start(cmd_box, False, False, 2)
        self.other_vbox.pack_start(buttons_box, False, False, 2)
        self.other_vbox.set_sensitive(False)

        self.add_child(chk_default, False, False, 2)
        self.add_child(chk_other, False, False, 2)
        self.add_child(self.other_vbox, False, False, 2)

        if current['cmd'] != '':
            self.other_vbox.set_sensitive(True)
            self.command.set_text(current['cmd'])
            chk_other.set_active(True)

        btn_browse.connect('clicked', self.__browse)
        btn_test.connect('clicked', self.__test)
        chk_default.connect('toggled', self.__activate, 'default')
        chk_other.connect('toggled', self.__activate, 'other')

        self.show_all()

    def __test(self, widget):
        cmd = self.command.get_text()
        if cmd != '':
            subprocess.Popen([cmd, 'http://turpial.org.ve/'])

    def __browse(self, widget):
        dia = Gtk.FileChooserDialog(
            title = _('Select the full path of your web browser'),
            parent=self.mainwin,
            action=Gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL,
                Gtk.STOCK_OK, Gtk.RESPONSE_OK))
        resp = dia.run()

        if resp == Gtk.RESPONSE_OK:
            self.command.set_text(dia.get_filename())
        dia.destroy()

    def __activate(self, widget, param):
        if param == 'default':
            self.other_vbox.set_sensitive(False)
            self.command.set_text('')
        else:
            self.other_vbox.set_sensitive(True)

    def get_config(self):
        return {
            'cmd': self.command.get_text()
        }

class AdvancedTab(GenericTab):
    def __init__(self, mainwin, current):
        GenericTab.__init__(
            self,
            _('Advanced options. Use it only if you know what you do'),
            current
        )
        self.mainwin = mainwin
        cache_size = self.mainwin.get_cache_size()
        label = "%s <span foreground='#999999'>%s</span>" % (
            i18n.get('delete_all_images_in_cache'),
            cache_size)
        self.cachelbl = Gtk.Label()
        self.cachelbl.set_use_markup(True)
        self.cachelbl.set_markup(label)
        self.cachelbl.set_alignment(0.0, 0.5)
        self.cachebtn = Gtk.Button(_('Clean cache'))
        self.cachebtn.set_size_request(110, -1)
        self.cachebtn.connect('clicked', self.__clean_cache)
        if cache_size == '0 B':
            self.cachebtn.set_sensitive(False)

        configlbl = Gtk.Label(_('Restore config to default'))
        configlbl.set_alignment(0.0, 0.5)
        self.configbtn = Gtk.Button(_('Restore config'))
        self.configbtn.set_size_request(110, -1)
        self.configbtn.connect('clicked', self.__restore_default_config)

        table = Gtk.Table(2, 2, False)
        table.attach(self.cachebtn, 0, 1, 0, 1, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(self.cachelbl, 1, 2, 0, 1, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, xpadding=5)
        table.attach(self.configbtn, 0, 1, 1, 2, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(configlbl, 1, 2, 1, 2, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, xpadding=5)

        timeout = int(self.current['socket-timeout'])
        show_avatars = True if self.current['show-user-avatars'] == 'on' else False

        self.timeout = TimeScroll(_('Timeout'), timeout, min=5, max=120,
            unit='sec', lbl_size=120)

        self.show_avatars = CheckBox(_('Load user avatars'), show_avatars, 
            _('Disable loading user avatars for slow connections'))
        self.show_avatars.set_sensitive(False)

        self.add_child(TitleLabel(_('Maintenance')), False, False, 2)
        self.add_child(table, False, False, 2)
        self.add_child(TitleLabel(_('Connection')), False, False, 2)
        self.add_child(self.timeout, False, False, 2)
        self.add_child(self.show_avatars, False, False, 2)
        self.show_all()

    def __clean_cache(self, widget):
        self.mainwin.delete_all_cache()
        self.cachebtn.set_sensitive(False)
        label = "%s <span foreground='#999999'>%s</span>" % (
            i18n.get('delete_all_images_in_cache'),
            self.mainwin.get_cache_size())
        self.cachelbl.set_markup(label)

    def __restore_default_config(self, widget):
        message = Gtk.MessageDialog(self.mainwin, Gtk.DIALOG_MODAL |
            Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_QUESTION,
            Gtk.BUTTONS_YES_NO)
        message.set_markup(i18n.get('restore_config_warning'))
        response = message.run()
        message.destroy()
        if response == Gtk.RESPONSE_YES:
            self.mainwin.restore_default_config()
            self.configbtn.set_sensitive(False)
            self.mainwin.main_quit(force=True)

    def get_config(self):
        show_avatars = 'on' if self.show_avatars.get_active() else 'off'

        return {
            'socket-timeout': int(self.timeout.value),
            'show-user-avatars': show_avatars,
        }

class ProxyTab(GenericTab):
    def __init__(self, current):
        GenericTab.__init__(
            self,
            _('Proxy settings for Turpial (Need Restart)'),
            current
        )

        self.server = ProxyField(_('Server/Port'), current['server'],
            current['port'])
        self.username = FormField(_('Username'), current['username'])
        self.password = FormField(_('Password'), current['password'], True)

        self.add_child(self.server, False, False, 2)
        self.add_child(self.username, False, False, 2)
        self.add_child(self.password, False, False, 2)

        self.show_all()

    def get_config(self):
        server, port = self.server.get_proxy()
        return {
            'username': self.username.get_text(),
            'password': self.password.get_text(),
            'server': server,
            'port': port,
        }

