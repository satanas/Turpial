# -*- coding: utf-8 -*-

""" Widget to update statuses in Turpial """
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from turpial.ui.lang import i18n

SPELLING = False
try:
    #import gtkspell
    SPELLING = False
except:
    pass

#from turpial.ui.Gtk.friendwin import FriendsWin
from turpial.ui.gtk.markuplabel import MarkupLabel

MAX_CHAR = 140

class UpdateBox(Gtk.Window):
    def __init__(self, base):
        Gtk.Window.__init__(self)

        self.blocked = False
        self.base = base
        self.title_caption = i18n.get('whats_happening')
        #self.set_resizable(False)
        self.set_default_size(500, 120)
        self.set_transient_for(base)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_gravity(Gdk.Gravity.STATIC)

        self.update_text = MessageTextView()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.update_text)

        self.btn_update = Gtk.Button(i18n.get('update'))
        self.btn_update.set_tooltip_text(i18n.get('update_status') + ' (Ctrl + Enter)')

        self.btn_short = Gtk.Button()
        self.btn_short.set_image(self.base.load_image('action-shorten.png'))
        self.btn_short.set_tooltip_text(i18n.get('short_urls'))

        self.btn_upload = Gtk.Button()
        self.btn_upload.set_image(self.base.load_image('action-upload.png'))
        self.btn_upload.set_tooltip_text(i18n.get('upload_image'))

        self.spinner = Gtk.Spinner()
        self.message = MarkupLabel(xalign=1)

        opt_box = Gtk.HBox()
        opt_box.pack_start(self.btn_upload, False, False, 1)
        opt_box.pack_start(self.btn_short, False, False, 1)

        opt_align = Gtk.Alignment()
        opt_align.set(0, -1, -1, -1)
        opt_align.add(opt_box)

        box = Gtk.HBox()
        box.pack_start(opt_align, False, False, 0)
        box.pack_start(self.message, True, True, 0)
        box.pack_start(self.spinner, False, False, 5)
        box.pack_start(self.btn_update, False, False, 2)
        buttonbox = Gtk.Alignment()
        buttonbox.set_property('xalign', 1)
        buttonbox.add(box)

        self.accounts = {}
        self.accbox = Gtk.HBox()
        for account in self.base.get_all_accounts():
            chk = Gtk.CheckButton(account.id_.split('-')[0])
            chk.set_margin_right(5)
            img = Gtk.Image()
            img.set_from_pixbuf(self.base.load_image(account.id_.split('-')[1] + '.png', True))
            self.accbox.pack_start(img, False, False, 0)
            self.accbox.pack_start(chk, False, False, 0)
            self.accounts[account.id_] = chk

        vbox = Gtk.VBox()
        vbox.pack_start(scroll, True, True, 3)
        vbox.pack_start(buttonbox, False, False, 0)
        vbox.pack_start(self.accbox, False, False, 0)
        vbox.set_margin_right(3)
        vbox.set_margin_left(3)

        self.add(vbox)

        _buffer = self.update_text.get_buffer()
        #self.connect('key-press-event', self.__detect_shortcut)
        _buffer.connect('changed', self.__count_chars)
        self.connect('delete-event', self.__unclose)
        #self.btn_upload.connect('clicked', self.__release)
        self.btn_short.connect('clicked', self.__short_url)
        self.btn_update.connect('clicked', self.__update_callback)
        #self.btn_url.connect('clicked', self.short_url)
        #self.btn_url.set_sensitive(False)
        self.update_text.connect('key-press-event', self.__on_key_pressed)

        if SPELLING:
            try:
                self.spell = Gtkspell.Spell (self.update_text)
            except Exception, e_msg:
                # FIXME: Usar el log
                print 'DEBUG:UI:Can\'t load Gtkspell -> %s' % e_msg
        else:
            # FIXME: Usar el log
            print 'DEBUG:UI:Can\'t load Gtkspell'

        self.__reset()
        self.__count_chars()

    def __on_key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Return' and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.__update_callback(widget)
            return True
        elif keyname == 'Escape':
            self.__unclose(widget)
            return True
        return False

    def __unclose(self, widget, event=None):
        if not self.blocked:
            if self.__count_chars() < 140:
                self.base.show_confirm_dialog(i18n.get('do_you_want_to_discard_message'), self.done)
            else:
                self.done()
        return True

    def __reset(self):
        self._account_id = None
        self._in_reply_id = None
        self._in_reply_user = None
        self._message = None
        self._direct_message_to = None
        self.message.set_markup('')

    def __count_chars(self, widget=None):
        _buffer = self.update_text.get_buffer()
        remain = MAX_CHAR - _buffer.get_char_count()
        self.set_title("%s (%i)" % (self.title_caption, remain))
        return remain

    def __update_callback(self, widget):
        status = self.update_text.get_text()
        accounts = []
        for key, chk in self.accounts.iteritems():
            if chk.get_active():
                accounts.append(key)

        # Validate basic variables
        if len(accounts) == 0:
            self.message.set_error_text(i18n.get('select_account_to_post'))
            return

        if status == '':
            self.message.set_error_text(i18n.get('you_must_write_something'))
            return

        if len(status) > MAX_CHAR:
            self.message.set_error_text(i18n.get('message_looks_like_testament'))
            return

        # Send direct message
        if self._direct_message_to:
            if len(accounts) > 1:
                self.message.set_error_text(i18n.get('can_send_message_to_one_account'))
            else:
                self.lock(i18n.get('sending_message'))
                self.base.direct_message(accounts[0], self._direct_message_to, status)
        # Send regular status
        else:
            self.lock(i18n.get('updating_status'))
            self.base.update_status(accounts, status, self._in_reply_id)

    def __show(self, message=None, status_id=None, account_id=None, reply_id=None, reply_user=None, ):
        # Check for new accounts
        for account in self.base.get_all_accounts():
            if not account.id_ in self.accounts:
                chk = Gtk.CheckButton(account.id_.split('-')[0])
                chk.set_margin_right(5)
                img = Gtk.Image()
                img.set_from_pixbuf(self.base.load_image(account.id_.split('-')[1] + '.png', True))
                self.accbox.pack_start(img, False, False, 0)
                self.accbox.pack_start(chk, False, False, 0)
                self.accounts[account.id_] = chk

        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_focus(self.update_text)

        if self._message:
            self.update_text.set_text(self._message)

        # TODO: Save the previous state of checkboxes
        if self._account_id:
            for key, account in self.accounts.iteritems():
                account.set_sensitive(False)
                account.set_active(False)
            self.accounts[self._account_id].set_active(True)

        self.show_all()
        self.unlock()
        self.__count_chars()

    def __short_url(self, widget):
        self.lock(i18n.get('shorting_urls'))
        message = self.update_text.get_text()
        if len(message) == 0:
            self.unlock(i18n.get('no_url_to_short'))
        else:
            self.base.autoshort_url(message)

    def close(self):
        self.__unclose(None)

    def show(self):
        self.title_caption = i18n.get('whats_happening')
        self.__show()

    def show_for_quote(self, message):
        self.title_caption = i18n.get('update_status')
        self._message = message
        self.__show()
        self.update_text.move_cursor(MessageTextView.CURSOR_START)

    def show_for_reply(self, in_reply_id, account_id, in_reply_user):
        self.title_caption = i18n.get('reply_status')
        self._in_reply_id = in_reply_id
        self._in_reply_user = in_reply_user
        self._account_id = account_id
        self._message = "%s " % (in_reply_user)
        self.__show()
        self.update_text.move_cursor(MessageTextView.CURSOR_END)

    def show_for_direct(self, account_id, username):
        self.title_caption = "%s @%s" % (i18n.get('send_message_to'), username)
        self._account_id = account_id
        self._direct_message_to = username
        self.__show()

    def show_for_reply_direct(self, in_reply_id, account_id, username):
        self.title_caption = "%s @%s" % (i18n.get('reply_message_to'), username)
        self._in_reply_id = in_reply_id
        self._account_id = account_id
        self._direct_message_to = username
        self.__show()

    def done(self, widget=None, event=None):
        self.update_text.clear()
        self.__reset()
        self.hide()
        return True

    def clear(self, widget):
        self.update_text.clear()
        self._direct_message_to = None

    def lock(self, msg):
        self.blocked = True
        self.update_text.set_sensitive(False)
        self.btn_update.set_sensitive(False)
        self.spinner.start()
        self.spinner.show()
        self.message.set_markup(msg)

        for key, account in self.accounts.iteritems():
            account.set_sensitive(False)

    def unlock(self, msg=None):
        self.blocked = False
        self.update_text.set_sensitive(True)
        self.btn_update.set_sensitive(True)
        self.spinner.stop()
        self.spinner.hide()

        if not self._account_id:
            for key, account in self.accounts.iteritems():
                account.set_sensitive(True)

        if msg:
            if msg != 'Unknown error':
                self.message.set_error_text(msg)
            else:
                self.message.set_error_text(i18n.get('i_couldnt_update_status'))
        else:
            self.message.set_text('')

        self.set_focus(self.update_text)


    def update_error(self, msg=None):
        self.unlock(msg)

    def broadcast_error(self, posted_accounts, err_accounts):
        errmsg = i18n.get('error_posting_to') % (', '.join(err_accounts))
        self.unlock(errmsg)
        for account_id in posted_accounts:
            self.accounts[account_id].set_sensitive(False)
            self.accounts[account_id].set_active(False)

    def update_after_short_url(self, response):
        if response.code == 815:
            self.unlock(i18n.get('url_already_short'))
        elif response.code == 812:
            self.unlock(i18n.get('no_url_to_short'))
        elif response.code > 0:
            self.unlock(i18n.get('couldnt_shrink_urls'))
        else:
            self.update_text.set_text(response.items)
            self.update_text.move_cursor(MessageTextView.CURSOR_END)
            self.unlock()


    """

    def show_friend_dialog(self, widget):
        f = FriendsWin(self, self.add_friend,
            self.base.request_friends_list())

    def add_friend(self, user):
        if user is None: return

        _buffer = self.update_text.get_buffer()
        end_offset = _buffer.get_property('cursor-position')
        start_offset = end_offset - 1

        end = _buffer.get_iter_at_offset(end_offset)
        start = _buffer.get_iter_at_offset(start_offset)
        text = _buffer.get_text(start, end)

        if (text != ' ') and (start_offset > 0):
            user = ' ' + user

        _buffer.insert_at_cursor(user)

        
    def __on_url_changed(self, widget):
        url_lenght = widget.get_text_length()
        if url_lenght == 0:
            self.btn_url.set_sensitive(False)
        else:
            self.btn_url.set_sensitive(True)
        return False

    def __detect_shortcut(self, widget, event=None):
        keyname = Gtk.gdk.keyval_name(event.keyval)

        if (event.state & Gtk.gdk.CONTROL_MASK) and keyname.lower() == 'f':
            self.show_friend_dialog(widget)
            return True
        elif (event.state & Gtk.gdk.CONTROL_MASK) and keyname.lower() == 'l':
            self.clear(widget)
            return True
        elif (event.state & Gtk.gdk.CONTROL_MASK) and keyname.lower() == 't':
            self.update(widget)
            return True
        return False
    """

class MessageTextView(Gtk.TextView):
    '''Class for the message textview (where user writes new messages)
    for chat/groupchat windows'''

    CURSOR_START = 1
    CURSOR_END = 2

    def __init__(self):
        GObject.GObject.__init__(self)
        Gtk.TextView.__init__(self)

        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.set_accepts_tab(False)

    def destroy(self):
        import gc
        GObject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')

    def set_text(self, message):
        self.get_buffer().set_text(message)

    def get_text(self):
        _buffer = self.get_buffer()
        start, end = _buffer.get_bounds()
        return _buffer.get_text(start, end, False)

    def move_cursor(self, position=CURSOR_END):
        _buffer = self.get_buffer()
        start_iter = _buffer.get_start_iter()
        end_iter = _buffer.get_end_iter()
        length = len(_buffer.get_text(start_iter, end_iter, False))

        if position == self.CURSOR_START:
            _buffer.place_cursor(start_iter)
        elif position == self.CURSOR_END:
            _buffer.place_cursor(end_iter)
        else:
            pass

