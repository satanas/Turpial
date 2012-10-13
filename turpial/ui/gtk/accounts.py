# -*- coding: utf-8 -*-

# GTK account manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2011

import logging

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from libturpial.common import LoginStatus

log = logging.getLogger('Gtk')

class AccountsDialog(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self)

        self.mainwin = parent
        self.set_title(i18n.get('accounts'))
        self.set_size_request(360, 320)
        self.set_resizable(False)
        self.set_icon(self.mainwin.load_image('turpial.png', True))
        self.set_transient_for(parent)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__key_pressed)

        self.model = Gtk.ListStore(GdkPixbuf.Pixbuf, str, GdkPixbuf.Pixbuf, str, object)
        self.model.set_sort_column_id(1, Gtk.SortType.DESCENDING)

        icon = Gtk.CellRendererPixbuf()
        icon.set_property('yalign', 0.5)
        icon.set_property('xalign', 0.5)
        icon.set_padding(7,7)

        account = Gtk.CellRendererText()
        account.set_property('wrap-width', 260)
        account.set_property('yalign', 0.5)
        account.set_property('xalign', 0)

        status = Gtk.CellRendererPixbuf()
        status.set_property('yalign', 0.5)
        status.set_property('xalign', 0.5)
        status.set_padding(7,7)

        column = Gtk.TreeViewColumn('accounts')
        column.set_alignment(0.0)
        column.pack_start(icon, False)
        column.pack_start(account, True)
        column.pack_start(status, False)
        column.add_attribute(account, 'markup', 1)
        column.add_attribute(icon, 'pixbuf', 0)
        column.add_attribute(status, 'pixbuf', 2)

        self.acc_list = Gtk.TreeView()
        self.acc_list.set_headers_visible(False)
        #self.acc_list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.acc_list.set_level_indentation(0)
        self.acc_list.set_resize_mode(Gtk.ResizeMode.IMMEDIATE)
        self.acc_list.set_model(self.model)
        self.acc_list.set_tooltip_column(0)
        self.acc_list.append_column(column)
        self.acc_list.connect("query-tooltip", self.__tooltip_query)
        ###self.acc_list.connect("cursor-changed", self.__on_select)

        select = self.acc_list.get_selection()
        select.connect('changed', self.__on_select)
        #self.acc_list.connect("button-release-event", self.__on_click)
        #self.click_handler = self.list.connect("cursor-changed", self.__on_select)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.acc_list)

        self.btn_add = Gtk.Button(i18n.get('add'))
        self.btn_login = Gtk.Button(i18n.get('login'))
        self.btn_login.set_sensitive(False)
        self.btn_delete = Gtk.Button(i18n.get('delete'))

        self.btn_add.connect('clicked', self.__on_add)
        self.btn_delete.connect('clicked', self.__on_delete)
        self.btn_login.connect('clicked', self.__on_login)

        box_button = Gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(Gtk.ButtonBoxStyle.END)
        box_button.pack_start(self.btn_login, False, False, 0)
        box_button.pack_start(self.btn_delete, False, False, 0)
        box_button.pack_start(self.btn_add, False, False, 0)

        vbox = Gtk.VBox(False)
        vbox.set_border_width(6)
        vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(box_button, False, False, 6)
        self.add(vbox)

        self.showed = False
        self.form = None

    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

    def __key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.__close(widget)

    def __get_selected(self):
        select = self.acc_list.get_selection()
        if select is None:
            return None

        model, row = select.get_selected()
        if row is None:
            return None

        acc = model.get_value(row, 4)
        return acc

    def __tooltip_query(self, treeview, x, y, mode, tooltip):
        path = treeview.get_path_at_pos(x, y)
        if path:
            treepath, column = path[:2]
            model = treeview.get_model()
            iter_ = model.get_iter(treepath)
            text = model.get_value(iter_, 3)
            tooltip.set_text(text)
        return False

    def __on_select(self, widget):
        acc = self.__get_selected()
        if acc is None:
            self.btn_delete.set_sensitive(False)
            self.btn_login.set_sensitive(False)
            self.btn_login.set_label(i18n.get('login'))
            return

        if acc.logged_in == LoginStatus.NONE:
            self.btn_login.set_label(i18n.get('login'))
            self.btn_login.set_sensitive(True)
            self.btn_delete.set_sensitive(True)
        elif acc.logged_in == LoginStatus.IN_PROGRESS:
            self.btn_login.set_label(i18n.get('in_progress'))
            self.btn_login.set_sensitive(False)
            self.btn_delete.set_sensitive(False)
        elif acc.logged_in == LoginStatus.DONE:
            self.btn_login.set_label(i18n.get('logged_in'))
            self.btn_login.set_sensitive(False)
            self.btn_delete.set_sensitive(True)

    def __on_delete(self, widget):
        acc = self.__get_selected()
        if acc is None:
            return
        self.__lock(True)
        self.mainwin.delete_account(acc.id_)

    def __on_login(self, widget):
        acc = self.__get_selected()
        if acc is None:
            return
        self.mainwin.single_login(acc.id_)
        self.btn_login.set_label(i18n.get('in_progress'))
        self.btn_login.set_sensitive(False)

    def __on_add(self, widget):
        self.form = AccountForm(self.mainwin, self)

    def __lock(self, value):
        value = not value
        self.acc_list.set_sensitive(value)
        self.btn_login.set_sensitive(value)
        self.btn_add.set_sensitive(value)
        self.btn_delete.set_sensitive(value)

    def update(self):
        if self.showed:
            self.model.clear()
            empty = True
            self.btn_login.set_sensitive(False)
            self.btn_delete.set_sensitive(False)
            for acc in self.mainwin.get_all_accounts():
                empty = False
                imagename = "%s.png" % acc.protocol_id
                pix = self.mainwin.load_image(imagename, True)
                username = "<span size='large'><b>%s</b></span>" % acc.username
                status = ''
                status_pix = None
                if acc.logged_in == LoginStatus.NONE:
                    status = i18n.get('disconnected')
                    status_pix = self.mainwin.load_image('mark-disconnected.png', True)
                elif acc.logged_in == LoginStatus.IN_PROGRESS:
                    status = i18n.get('connecting...')
                    status_pix = self.mainwin.load_image('mark-connecting.png', True)
                elif acc.logged_in == LoginStatus.DONE:
                    status = i18n.get('connected')
                    status_pix = self.mainwin.load_image('mark-connected.png', True)

                self.model.append([pix, username, status_pix, status, acc])
                del pix
                del status_pix
            if empty:
                self.btn_login.set_label(i18n.get('login'))
            else:
                self.acc_list.set_cursor((0, ))

    def cancel_login(self, message):
        if self.form:
            # Delete account if wasn't configured properly
            iter_ = self.model.get_iter_first()
            # If this is the first account you try to add delete it, else loop
            # throught the model and see which ones are registered but are not
            # in the model
            if iter_ is None:
                self.mainwin.delete_account(self.mainwin.get_accounts_list()[0])
            else:
                curr_acc = []
                while iter_:
                    acc = self.model.get_value(iter_, 4)
                    curr_acc.append(acc.id_)
                    iter_ = self.model.iter_next(iter_)

                for acc_id in self.mainwin.get_accounts_list():
                    if acc_id not in curr_acc:
                        self.mainwin.delete_account(acc_id)
            self.form.cancel(message)
        self.update()

    def done_login(self):
        if self.form:
            self.form.done()
            return True
        return False

    def done_delete(self):
        self.__lock(False)
        self.update()

    def status_message(self, message):
        if self.form:
            self.form.set_loading_message(message)

    def show(self):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.update()
            self.show_all()

    def quit(self):
        self.destroy()

# Update list after add account
class AccountForm(Gtk.Window):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        Gtk.Window.__init__(self)

        self.mainwin = mainwin
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title(i18n.get('create_account'))
        self.set_size_request(290, 200)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__key_pressed)

        plabel = Gtk.Label(i18n.get('protocol'))
        plabel.set_alignment(0, 0.5)

        plist = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        for p in self.mainwin.get_protocols_list():
            image = '%s.png' % p
            t_icon = self.mainwin.load_image(image, True)
            plist.append([t_icon, p, p])

        self.protocol = Gtk.ComboBox()
        self.protocol.set_model(plist)
        icon = Gtk.CellRendererPixbuf()
        txt = Gtk.CellRendererText()
        self.protocol.pack_start(icon, False)
        self.protocol.pack_start(txt, False)
        self.protocol.add_attribute(icon, 'pixbuf', 0)
        self.protocol.add_attribute(txt, 'markup', 1)

        self.username = Gtk.Entry()
        user_box = Gtk.HBox(False)
        user_box.pack_start(self.username, True, True, 0)

        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        pass_box = Gtk.HBox(True)
        pass_box.pack_start(self.password, True, True, 0)

        self.cred_label = Gtk.Label(i18n.get('user_and_password'))
        self.cred_label.set_alignment(0, 0.5)

        cred_box = Gtk.VBox(False)
        cred_box.pack_start(self.cred_label, False, False, 0)
        cred_box.pack_start(user_box, False, False, 0)
        cred_box.pack_start(pass_box, False, False, 0)

        self.btn_signin = Gtk.Button(i18n.get('signin'))

        self.spinner = Gtk.Spinner()
        self.waiting_label = Gtk.Label()
        waiting_box = Gtk.HBox()
        waiting_box.pack_start(self.spinner, False, False, 10)
        waiting_box.pack_start(self.waiting_label, True, False, 0)

        vbox = Gtk.VBox(False)
        vbox.set_border_width(12)
        vbox.pack_start(plabel, False, False, 0)
        vbox.pack_start(self.protocol, False, False, 0)
        vbox.pack_start(Gtk.EventBox(), False, False, 6)
        vbox.pack_start(cred_box, True, True, 0)
        vbox.pack_start(waiting_box, False, False, 0)
        vbox.pack_start(self.btn_signin, False, False, 6)

        self.add(vbox)
        self.show_all()

        self.protocol.connect('changed', self.__on_change_protocol)
        self.password.connect('activate', self.__on_sign_in)
        self.btn_signin.connect('clicked', self.__on_sign_in)

        self.protocol.set_active(0)
        self.working = False
        self.spinner.hide()

    def __close(self, widget, event=None):
        if not self.working:
            self.destroy()
            return False
        else:
            return True

    def __key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.__close(widget)

    def __on_change_protocol(self, widget):
        index = widget.get_active()
        model = widget.get_model()
        if index < 0:
            return

        self.waiting_label.set_text('')
        protocol = model[index][1]
        if protocol == 'twitter':
            self.username.set_visible(False)
            self.password.set_visible(False)
            self.cred_label.set_visible(False)
            self.btn_signin.grab_focus()
        elif protocol == 'identica':
            self.username.set_visible(True)
            self.password.set_visible(True)
            self.cred_label.set_visible(True)
            self.username.grab_focus()

    def __on_sign_in(self, widget):
        self.working = True
        username = self.username.get_text()
        passwd = self.password.get_text()
        model = self.protocol.get_model()
        pindex = self.protocol.get_active()
        protocol = model[pindex][1]

        # Validate
        if protocol == 'identica':
            if username == '' or passwd == '':
                self.waiting_label.set_text(i18n.get('credentials_could_not_be_empty'))
                return True

        self.__lock()
        self.waiting_label.set_text(i18n.get('connecting'))
        self.spinner.show()
        self.spinner.start()
        self.mainwin.save_account(username, protocol, passwd)

    def __lock(self):
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.protocol.set_sensitive(False)
        self.btn_signin.set_sensitive(False)

    def __unlock(self):
        self.username.set_sensitive(True)
        self.password.set_sensitive(True)
        self.protocol.set_sensitive(True)
        self.btn_signin.set_sensitive(True)

    def cancel(self, message):
        self.working = False
        self.__unlock()
        self.waiting_label.set_text(message)
        self.spinner.stop()
        self.spinner.hide()

    def set_loading_message(self, message):
        self.waiting_label.set_text(message)

    def done(self):
        self.working = False
        self.destroy()
