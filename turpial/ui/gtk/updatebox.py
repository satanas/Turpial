# -*- coding: utf-8 -*-

""" Widget to update statuses in Turpial """
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk

from turpial.ui.lang import i18n

SPELLING = False
try:
    import gtkspell
    SPELLING = True
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

        self.update_text = MessageTextView()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.update_text)

        self.btn_update = Gtk.Button(i18n.get('update'))
        self.btn_update.set_tooltip_text(i18n.get('update_status') + ' (Ctrl + Enter)')

        self.btn_short = Gtk.Button(i18n.get('short'))
        self.btn_short.set_tooltip_text(i18n.get('short_urls'))

        self.btn_upload = Gtk.Button(i18n.get('image'))
        self.btn_upload.set_tooltip_text(i18n.get('upload_image'))

        self.spinner = Gtk.Spinner()
        self.message = MarkupLabel(xalign=1)

        box = Gtk.HBox()
        box.pack_start(self.message, True, True, 0)
        box.pack_start(self.spinner, False, False, 5)
        box.pack_start(self.btn_upload, False, False, 2)
        box.pack_start(self.btn_short, False, False, 2)
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
        self.btn_upload.connect('clicked', self.__release)
        self.btn_short.connect('clicked', self.__release)
        self.btn_update.connect('clicked', self.__update_callback)
        #self.btn_url.connect('clicked', self.short_url)
        #self.btn_url.set_sensitive(False)
        #self.toolbox.connect('activate', self.show_options)
        #self.update_text.connect('mykeypress', self.__on_key_pressed)

        if SPELLING:
            try:
                self.spell = Gtkspell.Spell (self.update_text)
            except Exception, e_msg:
                # FIXME: Usar el log
                print 'DEBUG:UI:Can\'t load Gtkspell -> %s' % e_msg
        else:
            # FIXME: Usar el log
            print 'DEBUG:UI:Can\'t load Gtkspell'

        self.__reset_internal_var()
        self.__count_chars()

    def __unclose(self, widget, event=None):
        if not self.blocked:
            self.__done()
        return True

    def __reset_internal_var(self):
        self._account_id = None
        self._in_reply_id = None
        self._in_reply_user = None
        self._message = None
        self._direct_message_to = None
        self.message.set_markup('')

    def __release(self, widget):
        self.release()

    def __done(self, widget=None, event=None):
        _buffer = self.update_text.get_buffer()
        _buffer.set_text('')
        self.__reset_internal_var()
        self.hide()
        return True

    def __count_chars(self, widget=None):
        _buffer = self.update_text.get_buffer()
        remain = MAX_CHAR - _buffer.get_char_count()
        self.set_title("%s (%i)" % (self.title_caption, remain))

    def __update_callback(self, widget):
        _buffer = self.update_text.get_buffer()
        start, end = _buffer.get_bounds()
        tweet = _buffer.get_text(start, end, False)
        #if tweet == '':
        #    self.waiting.stop(error=True)
        #    self.lblerror.set_markup("<span size='small'>%s</span>" %
        #        _('Hey!... you must write something'))
        #    return
        #elif _buffer.get_char_count() > 140:
        #    self.waiting.stop(error=True)
        #    self.lblerror.set_markup("<span size='small'>%s</span>" %
        #        _('Hey!... that message looks like a testament'))
        #    return

        #self.base.request_update_status(tweet, self.in_reply_id)
        self.block(i18n.get('updating_status'))

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
            _buffer = self.update_text.get_buffer()
            _buffer.set_text(self._message)

        # TODO: Save the previous state of checkboxes
        if self._account_id:
            for key, account in self.accounts.iteritems():
                account.set_sensitive(False)
                account.set_active(False)
            self.accounts[self._account_id].set_active(True)

        self.show_all()
        self.release()
        self.__count_chars()

    def show(self):
        self.title_caption = i18n.get('whats_happening')
        self.__show()

    def show_for_quote(self, message):
        self.title_caption = i18n.get('update_status')
        self._message = message
        self.__show()

    def show_for_reply(self, in_reply_id, account_id, in_reply_user):
        self.title_caption = "%s @%s" % (i18n.get('in_reply_to'), in_reply_user)
        self._in_reply_id = in_reply_id
        self._in_reply_user = in_reply_user
        self._account_id = account_id
        self.__show()

    def show_for_direct(self,account_id, username):
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

    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        self._direct_message_to = None

    def block(self, msg):
        self.blocked = True
        self.update_text.set_sensitive(False)
        self.btn_update.set_sensitive(False)
        for key, account in self.accounts.iteritems():
            account.set_sensitive(False)
        self.spinner.start()
        self.spinner.show()
        self.message.set_markup(msg)

    def release(self, msg=None):
        self.blocked = False
        self.update_text.set_sensitive(True)
        self.btn_update.set_sensitive(True)
        if not self._account_id:
            for key, account in self.accounts.iteritems():
                account.set_sensitive(True)
        self.spinner.stop()
        self.spinner.hide()

        #if not msg:
        #    msg = _('Oh oh... I couldn\'t send the tweet')
        if msg:
            self.message.set_markup(msg)
        else:
            self.message.set_markup('')

        self.set_focus(self.update_text)

    """

    def show_friend_dialog(self, widget):
        f = FriendsWin(self, self.add_friend,
            self.base.request_friends_list())

    def short_url(self, widget):
        self.waiting.start()
        self.base.request_short_url(self.url.get_text(), self.update_shorten_url)

    def update_shorten_url(self, short):
        if short.err:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" %
                _('Oops... I couldn\'t shrink that URL'))
            return
        _buffer = self.update_text.get_buffer()
        end_offset = _buffer.get_property('cursor-position')
        start_offset = end_offset - 1

        end = _buffer.get_iter_at_offset(end_offset)
        start = _buffer.get_iter_at_offset(start_offset)
        text = _buffer.get_text(start, end)

        if (text != ' ') and (start_offset > 0):
            short.response = ' ' + short.response

        _buffer.insert_at_cursor(short.response)
        self.waiting.stop()
        self.lblerror.set_markup("")
        self.toolbox.set_expanded(False)
        self.set_focus(self.update_text)

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

     def __on_key_pressed(self, widget, keyval, keymod):
        if keyval == Gtk.keysyms.Return:
            self.update(widget)
        elif keyval == Gtk.keysyms.Escape:
            self.__unclose(widget)
        return False

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
    #__gsignals__ = dict(mykeypress=(gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, (int, Gtk.gdk.ModifierType)))

    def __init__(self):
        Gtk.TextView.__init__(self)

        #self.set_border_width(2)
        #self.set_left_margin(2)
        #self.set_right_margin(2)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.set_accepts_tab(False)

    def destroy(self):
        import gc
        #gobject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')

#Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Return, 0, 'mykeypress', int, Gtk.keysyms.Return, Gtk.gdk.ModifierType, 0)
#Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Escape, 0, 'mykeypress', int, Gtk.keysyms.Escape, Gtk.gdk.ModifierType, 0)
