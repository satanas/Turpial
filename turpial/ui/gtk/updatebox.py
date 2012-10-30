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
        self.set_resizable(False)
        self.set_size_request(500, 120)
        self.set_transient_for(base)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)


        self.update_text = MessageTextView()
        _buffer = self.update_text.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.update_text)

        updatebox = Gtk.HBox()
        updatebox.pack_start(scroll, True, True, 3)

        #self.btn_frn = Gtk.Button()
        #self.btn_frn.set_image(self.base.load_image('action-add-friends.png'))
        #self.btn_frn.set_tooltip_text(_('Add friends') + ' (Ctrl+F)')
        #self.btn_frn.set_relief(Gtk.RELIEF_NONE)

        self.btn_update = Gtk.Button(i18n.get('update'))
        self.btn_update.set_tooltip_text(i18n.get('update_status') + ' (Ctrl + Enter)')
        self.error_msg = MarkupLabel(xalign=1)

        box = Gtk.HBox()
        box.pack_start(self.error_msg, True, True, 0)
        box.pack_start(self.btn_update, False, False, 0)
        self.buttonbox = Gtk.Alignment()
        self.buttonbox.set(1, -1, -1, -1)
        self.buttonbox.add(box)

        self.spinner = Gtk.Spinner()
        self.progress_msg = MarkupLabel(xalign=1)

        self.progressbox = Gtk.HBox()
        self.progressbox.pack_start(self.progress_msg, True, True, 4)
        self.progressbox.pack_start(self.spinner, False, False, 5)

        self.spinner.start()

        vbox = Gtk.VBox(False)
        vbox.pack_start(updatebox, True, True, 2)
        vbox.pack_start(self.buttonbox, False, False, 2)
        vbox.pack_start(self.progressbox, False, False, 2)

        self.add(vbox)

        #self.connect('key-press-event', self.__detect_shortcut)
        #self.connect('delete-event', self.__unclose)
        _buffer.connect('changed', self.__count_chars)
        #self.btn_frn.connect('clicked', self.show_friend_dialog)
        #self.btn_clr.connect('clicked', self.clear)
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

        self.__count_chars()

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
            self.base.request_friends_list())

    def block(self, msg):
        self.blocked = True
        self.update_text.set_sensitive(False)
        #self.btn_clr.set_sensitive(False)
        self.btn_update.set_sensitive(False)
        #self.btn_url.set_sensitive(False)
        #self.btn_frn.set_sensitive(False)
        self.spinner.start()
        self.progress_msg.set_markup(msg)
        self.buttonbox.hide()
        self.progressbox.show()

    def release(self, msg=None):
        self.blocked = False
        self.update_text.set_sensitive(True)
        #self.btn_clr.set_sensitive(True)
        self.btn_update.set_sensitive(True)
        #self.btn_url.set_sensitive(True)
        #self.btn_frn.set_sensitive(True)
        self.spinner.stop()
        self.progress_msg.set_markup('')

        #if not msg:
        #    msg = _('Oh oh... I couldn\'t send the tweet')
        if msg:
            self.error_msg.set_error_text(msg)
        self.set_focus(self.update_text)
        self.progressbox.hide()
        self.buttonbox.show()

    def show(self, message=None, status_id=None, account_id=None, title=None):
        self.title = i18n.get('whats_happening')

        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_focus(self.update_text)
        #_buffer = self.update_text.get_buffer()
        #_buffer.set_text(message)
        self.show_all()

        self.release()

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

    def __count_chars(self, widget=None):
        _buffer = self.update_text.get_buffer()
        remain = MAX_CHAR - _buffer.get_char_count()
        self.set_title("%s (%i)" % (self.title_caption, remain))

    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        self.direct_message_to = None

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
    #__gsignals__ = dict(mykeypress=(gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, (int, Gtk.gdk.ModifierType)))

    def __init__(self):
        Gtk.TextView.__init__(self)

        self.set_border_width(2)
        self.set_left_margin(2)
        self.set_right_margin(2)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.set_accepts_tab(False)

    def destroy(self):
        import gc
        #gobject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')

#Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Return, 0, 'mykeypress', int, Gtk.keysyms.Return, Gtk.gdk.ModifierType, 0)
#Gtk.binding_entry_add_signal(MessageTextView, Gtk.keysyms.Escape, 0, 'mykeypress', int, Gtk.keysyms.Escape, Gtk.gdk.ModifierType, 0)
