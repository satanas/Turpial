# -*- coding: utf-8 -*-

"""Widget para subir imágenes desde Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Sep 27, 2010

import gtk
import gobject

SPELLING = False
try:
    import gtkspell
    SPELLING = True
except:
    pass

from turpial.ui.gtk.waiting import CairoWaiting
from turpial.ui.gtk.friendwin import FriendsWin

class UploadPicBox(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.filename = ''
        self.pic_url = ''
        self.blocked = False
        self.mainwin = parent
        
        #self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title(_('Upload picture'))
        self.set_resizable(False)
        self.set_size_request(300, 400)
        self.set_transient_for(parent)
        #self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        #self.btn_pic = gtk.Button(_('Click to select image'))
        self.btn_pic = gtk.Button()
        self.btn_pic.set_size_request(250, 250)
        pic_box = gtk.VBox(False)
        pic_box.pack_start(self.btn_pic, True, True, 0)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>%s</b></span>' % 
            _('Message'))
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        self.update_text = MessageTextView()
        self.update_text.set_border_width(2)
        self.update_text.set_left_margin(2)
        self.update_text.set_right_margin(2)
        self.update_text.set_wrap_mode(gtk.WRAP_WORD)
        buffer = self.update_text.get_buffer()
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.update_text)
        
        updatebox = gtk.HBox(False)
        updatebox.pack_start(scroll, True, True, 3)
        
        self.btn_clr = gtk.Button()
        self.btn_clr.set_image(self.mainwin.load_image('action-clear.png'))
        self.btn_clr.set_tooltip_text(_('Clear all') + ' (Ctrl+L)')
        self.btn_clr.set_relief(gtk.RELIEF_NONE)
        
        self.btn_frn = gtk.Button()
        self.btn_frn.set_image(self.mainwin.load_image('action-add-friends.png'))
        self.btn_frn.set_tooltip_text(_('Add friends') + ' (Ctrl+F)')
        self.btn_frn.set_relief(gtk.RELIEF_NONE)
        
        self.btn_upd = gtk.Button(_('Upload'))
        self.btn_upd.set_tooltip_text(_('Update your status') + ' (Ctrl+T)')
        
        top = gtk.HBox(False)
        top.pack_start(self.label, True, True, 5)
        top.pack_start(self.num_chars, False, False, 5)
        
        self.waiting = CairoWaiting(parent)
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        error_align = gtk.Alignment(xalign=0.0)
        error_align.add(self.lblerror)
        
        buttonbox = gtk.HBox(False)
        buttonbox.pack_start(self.btn_frn, False, False, 0)
        buttonbox.pack_start(self.btn_clr, False, False, 0)
        buttonbox.pack_start(gtk.HSeparator(), False, False, 2)
        buttonbox.pack_start(self.btn_upd, False, False, 0)
        abuttonbox = gtk.Alignment(1, 0.5)
        abuttonbox.add(buttonbox)
        
        bottom = gtk.HBox(False)
        bottom.pack_start(self.waiting, False, False, 5)
        bottom.pack_start(error_align, True, True, 4)
        #bottom.pack_start(abuttonbox, True, True, 5)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(pic_box, False, False, 2)
        vbox.pack_start(top, False, False, 2)
        vbox.pack_start(updatebox, True, True, 2)
        vbox.pack_start(abuttonbox, False, False, 2)
        vbox.pack_start(bottom, False, False, 2)
        
        self.add(vbox)
        
        self.connect('key-press-event', self.__detect_shortcut)
        self.connect('delete-event', self.__unclose)
        buffer.connect('changed', self.count_chars)
        self.btn_frn.connect('clicked', self.show_friend_dialog)
        self.btn_clr.connect('clicked', self.clear)
        self.btn_upd.connect('clicked', self.upload)
        self.btn_pic.connect('clicked', self.choose_pic)
        self.update_text.connect('mykeypress', self.__on_key_pressed)
        
        if SPELLING: 
            try:
                self.spell = gtkspell.Spell (self.update_text)
            except Exception, e_msg:
                # FIXME: Usar el log
                print 'DEBUG:UI:Can\'t load gtkspell -> %s' % e_msg
        else:
            # FIXME: Usar el log
            print 'DEBUG:UI:Can\'t load gtkspell'
    
    def __on_key_pressed(self, widget, keyval, keymod):
        if keyval == gtk.keysyms.Return:
            self.update(widget)
        elif keyval == gtk.keysyms.Escape:
            self.__unclose(widget)
        return False
    
    def __detect_shortcut(self, widget, event=None):
        keyname = gtk.gdk.keyval_name(event.keyval)
        
        if (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'f':
            self.show_friend_dialog(widget)
            return True
        elif (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'l':
            self.clear(widget)
            return True
        elif (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'u':
            self.update(widget)
            return True
        return False
        
    def __unclose(self, widget, event=None):
        if not self.blocked:
            self.done()
        return True
        
    def _do_tweet(self):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = "%s - %s" % (self.pic_url, buffer.get_text(start, end))
        if len(tweet) > 140:
            tweet = tweet[:137] + '...'
        self.mainwin.request_update_status(tweet, None)
        
    def show_friend_dialog(self, widget):
        f = FriendsWin(self, self.add_friend, 
            self.mainwin.request_friends_list())
        
    def block(self):
        self.blocked = True
        self.update_text.set_sensitive(False)
        self.btn_clr.set_sensitive(False)
        self.btn_upd.set_sensitive(False)
        self.btn_frn.set_sensitive(False)
        self.btn_pic.set_sensitive(False)
        
    def release(self, msg=None):
        self.blocked = False
        self.update_text.set_sensitive(True)
        self.btn_clr.set_sensitive(True)
        self.btn_upd.set_sensitive(True)
        self.btn_frn.set_sensitive(True)
        self.btn_pic.set_sensitive(True)
        self.waiting.stop(error=True)
        
        if not msg:
            msg = _('Oh oh... I couldn\'t upload the pic')
        
        self.lblerror.set_markup("<span size='small'>%s</span>" % msg)
        self.set_focus(self.update_text)
        
    def show(self):
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_focus(self.update_text)
        buffer = self.update_text.get_buffer()
        buffer.set_text('')
        self.show_all()
        
    def done(self, widget=None, event=None):
        buffer = self.update_text.get_buffer()
        buffer.set_text('')
        self.lblerror.set_markup('')
        self.waiting.stop()
        self.btn_pic.set_image(gtk.Image())
        #self.btn_pic.set_label(_('Click to select image'))
        self.filename = ''
        self.pic_url = ''
        self.hide()
        return True
        
    def count_chars(self, widget):
        buffer = self.update_text.get_buffer()
        remain = 140 - buffer.get_char_count()
        
        if remain >= 20:
            color = "#999"
        elif 0 < remain < 20:
            color = "#d4790d"
        else:
            color = "#D40D12"
        
        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))
        
    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        
    def upload(self, widget):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = buffer.get_text(start, end)
        if buffer.get_char_count() > 140:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" % 
                _('Hey!... that message looks like a testament'))
            return
        
        self.waiting.start()
        if self.pic_url == '':
            self.mainwin.request_upload_pic(self.filename, tweet,
                self.update_uploaded_pic)
        else:
            self._do_tweet()
        self.block()
        
    def choose_pic(self, widget):
        filtro = gtk.FileFilter()
        filtro.set_name('PNG, JPEG & GIF Images')
        filtro.add_pattern('*.png')
        filtro.add_pattern('*.gif')
        filtro.add_pattern('*.jpg')
        filtro.add_pattern('*.jpeg')
        filtro.add_pattern('*.PNG')
        filtro.add_pattern('*.GIF')
        filtro.add_pattern('*.JPG')
        filtro.add_pattern('*.JPG')
        
        dia = gtk.FileChooserDialog(title=_('Select image to upload'),
            parent=self, action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.add_filter(filtro)
        resp = dia.run()
        
        if resp == gtk.RESPONSE_OK:
            self.filename = dia.get_filename()
            pixbuf = self.mainwin.load_avatar('', self.filename)
            rpixbuf = pixbuf.scale_simple(250, 250, gtk.gdk.INTERP_BILINEAR)
            avatar = gtk.Image()
            avatar.set_from_pixbuf(rpixbuf)
            self.btn_pic.set_image(avatar)
            #self.btn_pic.set_label('')
            del pixbuf
            del rpixbuf
        dia.destroy()
        
    def update_uploaded_pic(self, pic_url):
        if pic_url.err or not pic_url.response:
            self.release(pic_url.err_msg)
            return
        
        self.pic_url = pic_url.response
        self._do_tweet()
    
    def add_friend(self, user):
        if user is None: return
        
        buffer = self.update_text.get_buffer()
        end_offset = buffer.get_property('cursor-position')
        start_offset = end_offset - 1
        
        end = buffer.get_iter_at_offset(end_offset)
        start = buffer.get_iter_at_offset(start_offset)
        text = buffer.get_text(start, end)
        
        if (text != ' ') and (start_offset > 0):
            user = ' ' + user
        
        buffer.insert_at_cursor(user)

class MessageTextView(gtk.TextView):
    '''Class for the message textview (where user writes new messages)
    for chat/groupchat windows'''
    __gsignals__ = dict(mykeypress=(gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, (int, gtk.gdk.ModifierType)))
        
    def __init__(self):
        gtk.TextView.__init__(self)
        
        self.set_border_width(2)
        self.set_left_margin(2)
        self.set_right_margin(2)
        self.set_wrap_mode(gtk.WRAP_WORD)
        self.set_accepts_tab(False)

    def destroy(self):
        import gc
        gobject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')
        
if gobject.pygtk_version < (2, 8, 0):
    gobject.type_register(MessageTextView)

gtk.binding_entry_add_signal(MessageTextView, gtk.keysyms.Return, 0, 'mykeypress', int, gtk.keysyms.Return, gtk.gdk.ModifierType, 0)
gtk.binding_entry_add_signal(MessageTextView, gtk.keysyms.Escape, 0, 'mykeypress', int, gtk.keysyms.Escape, gtk.gdk.ModifierType, 0)
