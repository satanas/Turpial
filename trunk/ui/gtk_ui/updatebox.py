# -*- coding: utf-8 -*-

# Widget para actualizar el estado del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk

from waiting import*
from ui import util as util

class UpdateBox(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.blocked = False
        self.mainwin = parent
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title('Update Status')
        self.set_resizable(False)
        #self.set_default_size(500, 120)
        self.set_size_request(500, 150)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>What\'s happening?</b></span>')
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        self.update_text = gtk.TextView()
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
        self.btn_url = gtk.Button('Shorten URL')
        self.btn_url.set_tooltip_text('Shorten URL')
        #self.btn_url.set_relief(gtk.RELIEF_NONE)
        #self.btn_url.set_image(util.load_image('cut.png'))
        
        btn_pic = gtk.Button('Upload Pic')
        btn_pic.set_tooltip_text('Upload Pic')
        btn_pic.set_sensitive(False)
        #btn_pic.set_relief(gtk.RELIEF_NONE)
        #btn_pic.set_image(util.load_image('photos.png'))
        
        tools = gtk.HBox(False)
        tools.pack_start(self.url, True, True, 3)
        tools.pack_start(self.btn_url, False, False)
        tools.pack_start(gtk.HSeparator(), False, False)
        tools.pack_start(btn_pic, False, False, 3)
        
        self.toolbox = gtk.Expander()
        self.toolbox.set_label('Opciones')
        self.toolbox.set_expanded(False)
        self.toolbox.add(tools)
        
        self.btn_clr = gtk.Button()
        self.btn_clr.set_image(util.load_image('clear.png'))
        self.btn_clr.set_tooltip_text('Clear Box')
        self.btn_clr.set_relief(gtk.RELIEF_NONE)
        self.btn_upd = gtk.Button('Tweet')
        chk_short = gtk.CheckButton('Autocortado de URLs')
        chk_short.set_sensitive(False)
        
        top = gtk.HBox(False)
        top.pack_start(self.label, True, True, 5)
        top.pack_start(self.num_chars, False, False, 5)
        
        self.waiting = CairoWaiting(self)
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
        btn_pic.connect('clicked', self.upload_pic)
        self.toolbox.connect('activate', self.show_options)
    
    def __unclose(self, widget, event):
        if not self.blocked: self.done()
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
        self.lblerror.set_markup("<span size='small'>No se pudo enviar el tweet</span>")
        
    def show(self, text, id, user):
        self.in_reply_id = id
        self.in_reply_user = user
        if id != '' and user != '':
            self.label.set_markup('<span size="medium"><b>Reply to %s</b></span>' % user)
        
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
        self.label.set_markup('<span size="medium"><b>What\'s happening?</b></span>')
        self.waiting.stop()
        self.toolbox.set_expanded(False)
        self.hide()
        return True
        
    def count_chars(self, widget):
        buffer = self.update_text.get_buffer()
        remain = 140 - buffer.get_char_count()
        
        if remain >= 20: color = "#999"
        elif 0 < remain < 20: color = "#d4790d"
        else: color = "#D40D12"
        
        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))
        
    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        
    def update(self, widget):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = buffer.get_text(start, end)
        if tweet == '': 
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>Debe escribir algo</span>")
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
            self.lblerror.set_markup("<span size='small'>Error intentando cortar la URL</span>")
            return
        buffer = self.update_text.get_buffer()
        end_offset = buffer.get_property('cursor-position')
        start_offset = end_offset - 1
        
        end = buffer.get_iter_at_offset(end_offset)
        start = buffer.get_iter_at_offset(start_offset)
        text = buffer.get_text(start, end)
        
        if (text != ' ') and (start_offset > 0): short = ' ' + short
        
        buffer.insert_at_cursor(short)
        self.waiting.stop()
        self.lblerror.set_markup("")
        self.toolbox.set_expanded(False)
        
    def upload_pic(self, widget):
        filtro = gtk.FileFilter()
        filtro.set_name('PNG, JPEG & GIF Images')
        filtro.add_pattern('*.png')
        filtro.add_pattern('*.gif')
        filtro.add_pattern('*.jpg')
        filtro.add_pattern('*.jpeg')
        
        dia = gtk.FileChooserDialog(title='Seleccione la imagen que desea subir',
            parent=self, action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.add_filter(filtro)
        resp = dia.run()
        
        if resp == gtk.RESPONSE_OK:
            log.debug('Subiendo Imagen: %s' % dia.get_filename())
            ## self.mainwin.request_upload_pic(dia.get_filename())
        dia.destroy()
        
    def show_options(self, widget, event=None):
        self.url.set_text('')
        self.url.grab_focus()
