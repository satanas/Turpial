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

class UpdateBox(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self)

        self.blocked = False
        self.mainwin = parent
        self.set_title(i18n.get('whats_happening'))
        self.set_resizable(False)
        #self.set_default_size(500, 120)
        self.set_size_request(500, 150)
        self.set_transient_for(parent)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        self.label = Gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>%s</b></span>' % self.what)
        self.label.set_justify(Gtk.JUSTIFY_LEFT)

        self.num_chars = Gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')

        self.update_text = MessageTextView()
        self.update_text.set_border_width(2)
        self.update_text.set_left_margin(2)
        self.update_text.set_right_margin(2)
        self.update_text.set_wrap_mode(Gtk.WRAP_WORD)
        _buffer = self.update_text.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.update_text)

        updatebox = Gtk.HBox(False)
        updatebox.pack_start(scroll, True, True, 3)

        self.btn_clr = Gtk.Button()
        self.btn_clr.set_image(self.mainwin.load_image('action-clear.png'))
        self.btn_clr.set_tooltip_text(_('Clear all') + ' (Ctrl+L)')
        self.btn_clr.set_relief(Gtk.RELIEF_NONE)

        self.btn_frn = Gtk.Button()
        self.btn_frn.set_image(self.mainwin.load_image('action-add-friends.png'))
        self.btn_frn.set_tooltip_text(_('Add friends') + ' (Ctrl+F)')
        self.btn_frn.set_relief(Gtk.RELIEF_NONE)

        self.btn_upd = Gtk.Button(_('Tweet'))
        self.btn_upd.set_tooltip_text(_('Update your status') + ' (Ctrl+T)')
        chk_short = Gtk.CheckButton(_('Autoshort URLs'))
        chk_short.set_sensitive(False)

        top = Gtk.HBox(False)
        top.pack_start(self.label, True, True, 5)
        top.pack_start(self.num_chars, False, False, 5)

        self.waiting = CairoWaiting(parent)
        self.lblerror = Gtk.Label()
        self.lblerror.set_use_markup(True)
        error_align = Gtk.Alignment(xalign=0.0)
        error_align.add(self.lblerror)

        buttonbox = Gtk.HBox(False)
        #buttonbox.pack_start(chk_short, False, False, 0)
        buttonbox.pack_start(self.btn_frn, False, False, 0)
        buttonbox.pack_start(self.btn_clr, False, False, 0)
        buttonbox.pack_start(Gtk.HSeparator(), False, False, 2)
        buttonbox.pack_start(self.btn_upd, False, False, 0)
        abuttonbox = Gtk.Alignment(1, 0.5)
        abuttonbox.add(buttonbox)

        bottom = Gtk.HBox(False)
        bottom.pack_start(self.waiting, False, False, 5)
        bottom.pack_start(error_align, True, True, 4)
        bottom.pack_start(abuttonbox, True, True, 5)

        vbox = Gtk.VBox(False)
        vbox.pack_start(top, False, False, 2)
        vbox.pack_start(updatebox, True, True, 2)
        vbox.pack_start(bottom, False, False, 2)
        vbox.pack_start(self.toolbox, False, False, 2)

        self.add(vbox)

        self.connect('key-press-event', self.__detect_shortcut)
        self.connect('delete-event', self.__unclose)
        _buffer.connect('changed', self.count_chars)
        self.btn_frn.connect('clicked', self.show_friend_dialog)
        self.btn_clr.connect('clicked', self.clear)
        self.btn_upd.connect('clicked', self.update)
        self.btn_url.connect('clicked', self.short_url)
        self.btn_url.set_sensitive(False)
        self.toolbox.connect('activate', self.show_options)
        self.update_text.connect('mykeypress', self.__on_key_pressed)

        if SPELLING:
            try:
                self.spell = Gtkspell.Spell (self.update_text)
            except Exception, e_msg:
                # FIXME: Usar el log
                print 'DEBUG:UI:Can\'t load Gtkspell -> %s' % e_msg
        else:
            # FIXME: Usar el log
            print 'DEBUG:UI:Can\'t load Gtkspell'

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

    def __unclose(self, widget, event=None):
        if not self.blocked:
            self.done()
        return True

    def show_friend_dialog(self, widget):
        f = FriendsWin(self, self.add_friend,
            self.mainwin.request_friends_list())

    def block(self):
        self.blocked = True
        self.update_text.set_sensitive(False)
        self.toolbox.set_sensitive(False)
        self.btn_clr.set_sensitive(False)
        self.btn_upd.set_sensitive(False)
        self.btn_url.set_sensitive(False)
        self.btn_frn.set_sensitive(False)

    def release(self, msg=None):
        self.blocked = False
        self.update_text.set_sensitive(True)
        self.toolbox.set_sensitive(True)
        self.btn_clr.set_sensitive(True)
        self.btn_upd.set_sensitive(True)
        self.btn_url.set_sensitive(True)
        self.btn_frn.set_sensitive(True)
        self.waiting.stop(error=True)

        if not msg:
            msg = _('Oh oh... I couldn\'t send the tweet')

        self.lblerror.set_markup("<span size='small'>%s</span>" % msg)
        self.set_focus(self.update_text)

    def show(self, message=None, status_id=None, account_id=None, title=None):
        self.title = i18n.get('whats_happening')

        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_focus(self.update_text)
        _buffer = self.update_text.get_buffer()
        _buffer.set_text(text)
        self.show_all()

    def show_for_quote(self, message):
        self.title = i18n.get('update_status')

    def show_for_reply(self, status_id, account_id, reply_to):
        self.title = i18n.get('reply_status')

    def show_for_direct(self,account_id, username):
        self.title = i18n.get('send_message_to')

    def show_for_reply_direct(self, status_id, account_id, username):
        self.title = i18n.get('send_message_to')

    def done(self, widget=None, event=None):
        _buffer = self.update_text.get_buffer()
        _buffer.set_text('')
        self.url.set_text('')
        self.lblerror.set_markup('')
        self.label.set_markup(u'<span size="medium"><b>%s</b></span>' %
            self.what)
        self.waiting.stop()
        self.toolbox.set_expanded(False)
        self.in_reply_id = None
        self.in_reply_user = None
        self.hide()
        return True

    def count_chars(self, widget):
        _buffer = self.update_text.get_buffer()
        remain = 140 - _buffer.get_char_count()

        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))

    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        self.direct_message_to = None

    def update(self, widget):
        _buffer = self.update_text.get_buffer()
        start, end = _buffer.get_bounds()
        tweet = _buffer.get_text(start, end)
        if tweet == '':
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" %
                _('Hey!... you must write something'))
            return
        elif _buffer.get_char_count() > 140:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" %
                _('Hey!... that message looks like a testament'))
            return

        self.waiting.start()
        self.mainwin.request_update_status(tweet, self.in_reply_id)
        self.block()

    def short_url(self, widget):
        self.waiting.start()
        self.mainwin.request_short_url(self.url.get_text(), self.update_shorten_url)

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

    def show_options(self, widget, event=None):
        self.url.set_text('')
        self.url.grab_focus()

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

class MessageTextView(Gtk.TextView):
    '''Class for the message textview (where user writes new messages)
    for chat/groupchat windows'''
    __gsignals__ = dict(mykeypress=(gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, (int, Gtk.gdk.ModifierType)))

    def __init__(self):
        Gtk.TextView.__init__(self)

        self.set_border_width(2)
        self.set_left_margin(2)
        self.set_right_margin(2)
        self.set_wrap_mode(Gtk.WRAP_WORD)
        self.set_accepts_tab(False)

    def destroy(self):
        import gc
        gobject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')

Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Return, 0, 'mykeypress', int, Gtk.keysyms.Return, Gtk.gdk.ModifierType, 0)
Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Escape, 0, 'mykeypress', int, Gtk.keysyms.Escape, Gtk.gdk.ModifierType, 0)
