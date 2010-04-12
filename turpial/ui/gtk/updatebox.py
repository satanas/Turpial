# -*- coding: utf-8 -*-

"""Widget para actualizar el estado del Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk
import gobject

SPELLING = False
try:
    import gtkspell
    SPELLING = True
except:
    pass

from turpial.ui.gtk.waiting import CairoWaiting

class UpdateBox(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.what = _('What is happening?')
        self.blocked = False
        self.mainwin = parent
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title(_('Update status'))
        self.set_resizable(False)
        #self.set_default_size(500, 120)
        self.set_size_request(500, 150)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>%s</b></span>' % 
            self.what)
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        #self.update_text = gtk.TextView()
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
        
        self.url = gtk.Entry()
        self.btn_url = gtk.Button(_('Shorten URL'))
        self.btn_url.set_tooltip_text(_('Shorten URL'))
        
        self.btn_pic = gtk.Button(_('Upload image'))
        self.btn_pic.set_tooltip_text(_('Upload image'))
        
        tools = gtk.HBox(False)
        tools.pack_start(self.url, True, True, 3)
        tools.pack_start(self.btn_url, False, False)
        tools.pack_start(gtk.HSeparator(), False, False)
        tools.pack_start(self.btn_pic, False, False, 3)
        
        self.toolbox = gtk.Expander()
        self.toolbox.set_label(_('Options'))
        self.toolbox.set_expanded(False)
        self.toolbox.add(tools)
        
        self.btn_clr = gtk.Button()
        self.btn_clr.set_image(self.mainwin.load_image('clear.png'))
        self.btn_clr.set_tooltip_text(_('Clear all'))
        self.btn_clr.set_relief(gtk.RELIEF_NONE)
        self.btn_upd = gtk.Button(_('Tweet'))
        chk_short = gtk.CheckButton(_('Autoshort URLs'))
        chk_short.set_sensitive(False)
        
        top = gtk.HBox(False)
        top.pack_start(self.label, True, True, 5)
        top.pack_start(self.num_chars, False, False, 5)
        
        self.waiting = CairoWaiting(parent)
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        error_align = gtk.Alignment(xalign=0.0)
        error_align.add(self.lblerror)
        
        buttonbox = gtk.HBox(False)
        buttonbox.pack_start(chk_short, False, False, 0)
        buttonbox.pack_start(self.btn_clr, False, False, 0)
        buttonbox.pack_start(gtk.HSeparator(), False, False, 2)
        buttonbox.pack_start(self.btn_upd, False, False, 0)
        abuttonbox = gtk.Alignment(1, 0.5)
        abuttonbox.add(buttonbox)
        
        bottom = gtk.HBox(False)
        bottom.pack_start(self.waiting, False, False, 5)
        bottom.pack_start(error_align, True, True, 4)
        bottom.pack_start(abuttonbox, True, True, 5)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(top, False, False, 2)
        vbox.pack_start(updatebox, True, True, 2)
        vbox.pack_start(bottom, False, False, 2)
        vbox.pack_start(self.toolbox, False, False, 2)
        
        self.add(vbox)
        
        self.connect('delete-event', self.__unclose)
        buffer.connect('changed', self.count_chars)
        self.btn_clr.connect('clicked', self.clear)
        self.btn_upd.connect('clicked', self.update)
        self.btn_url.connect('clicked', self.short_url)
        self.btn_pic.connect('clicked', self.upload_pic)
        self.toolbox.connect('activate', self.show_options)
        self.update_text.connect('mykeypress', self.__on_key_pressed)
        
        if SPELLING: 
            self.spell = gtkspell.Spell (self.update_text)
        else:
            print 'DEBUG:UI:Can\'t load gtkspell'
    
    def __on_key_pressed(self, widget, keyval, keymod):
        if keyval == gtk.keysyms.Return:
            self.update(widget)
        elif keyval == gtk.keysyms.Escape:
            self.__unclose(widget)
        return False
            
    def __unclose(self, widget, event=None):
        if not self.blocked:
            self.done()
        return True
        
    def block(self):
        self.blocked = True
        self.update_text.set_sensitive(False)
        self.toolbox.set_sensitive(False)
        self.btn_clr.set_sensitive(False)
        self.btn_upd.set_sensitive(False)
        self.btn_url.set_sensitive(False)
        
    def release(self):
        self.blocked = False
        self.update_text.set_sensitive(True)
        self.toolbox.set_sensitive(True)
        self.btn_clr.set_sensitive(True)
        self.btn_upd.set_sensitive(True)
        self.btn_url.set_sensitive(True)
        self.waiting.stop(error=True)
        self.lblerror.set_markup("<span size='small'>%s</span>" % 
            _('Oh oh... I couldn\'t send the tweet'))
        self.set_focus(self.update_text)
        
    def show(self, text, id, user):
        self.in_reply_id = id
        self.in_reply_user = user
        if id != '' and user != '':
            self.label.set_markup('<span size="medium"><b>%s %s</b></span>' % 
                (_('In reply to'), user))
        
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_focus(self.update_text)
        buffer = self.update_text.get_buffer()
        buffer.set_text(text)
        self.show_all()
        
    def done(self, widget=None, event=None):
        buffer = self.update_text.get_buffer()
        buffer.set_text('')
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
        
    def update(self, widget):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = buffer.get_text(start, end)
        if tweet == '': 
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" % 
                _('Eyy... you must write something'))
            return
        
        self.waiting.start()
        self.mainwin.request_update_status(tweet, self.in_reply_id)
        self.block()
        
    def short_url(self, widget):
        self.waiting.start()
        self.mainwin.request_short_url(self.url.get_text(), self.update_shorten_url)
        
    def update_shorten_url(self, short):
        if short is None:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" % 
                _('Oops... I couldn\'t shrink that URL'))
            return
        buffer = self.update_text.get_buffer()
        end_offset = buffer.get_property('cursor-position')
        start_offset = end_offset - 1
        
        end = buffer.get_iter_at_offset(end_offset)
        start = buffer.get_iter_at_offset(start_offset)
        text = buffer.get_text(start, end)
        
        if (text != ' ') and (start_offset > 0):
            short = ' ' + short
        
        buffer.insert_at_cursor(short)
        self.waiting.stop()
        self.lblerror.set_markup("")
        self.toolbox.set_expanded(False)
        self.set_focus(self.update_text)
        
    def upload_pic(self, widget):
        filtro = gtk.FileFilter()
        filtro.set_name('PNG, JPEG & GIF Images')
        filtro.add_pattern('*.png')
        filtro.add_pattern('*.gif')
        filtro.add_pattern('*.jpg')
        filtro.add_pattern('*.jpeg')
        
        dia = gtk.FileChooserDialog(title=_('Select image to upload'),
            parent=self, action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.add_filter(filtro)
        resp = dia.run()
        
        if resp == gtk.RESPONSE_OK:
            self.waiting.start()
            self.mainwin.request_upload_pic(dia.get_filename(),
                                            self.update_uploaded_pic)
        dia.destroy()
        
    def update_uploaded_pic(self, pic_url):
        if pic_url is None:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>%s</span>" % 
                _('Oops... I couldn\'t upload that image'))
            return
        buffer = self.update_text.get_buffer()
        end_offset = buffer.get_property('cursor-position')
        start_offset = end_offset - 1
        
        end = buffer.get_iter_at_offset(end_offset)
        start = buffer.get_iter_at_offset(start_offset)
        text = buffer.get_text(start, end)
        
        if (text != ' ') and (start_offset > 0):
            pic_url = ' ' + pic_url
        
        buffer.insert_at_cursor(pic_url)
        self.waiting.stop()
        self.lblerror.set_markup("")
        self.toolbox.set_expanded(False)
        self.set_focus(self.update_text)
        
    def show_options(self, widget, event=None):
        self.url.set_text('')
        self.url.grab_focus()

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

    def destroy(self):
        import gc
        gobject.idle_add(lambda:gc.collect())

    def clear(self, widget=None):
        self.get_buffer().set_text('')
        
if gobject.pygtk_version < (2, 8, 0):
    gobject.type_register(MessageTextView)

gtk.binding_entry_add_signal(MessageTextView, gtk.keysyms.Return, 0, 'mykeypress', int, gtk.keysyms.Return, gtk.gdk.ModifierType, 0)
gtk.binding_entry_add_signal(MessageTextView, gtk.keysyms.Escape, 0, 'mykeypress', int, gtk.keysyms.Escape, gtk.gdk.ModifierType, 0)
