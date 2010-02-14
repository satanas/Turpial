# -*- coding: utf-8 -*-

# Formulario para mostrar/actualizar el perfil del usuario en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import gtk

from core.ui import util as util

class UserForm(gtk.VBox):
    def __init__(self, mainwin, label='', profile=None):
        gtk.VBox.__init__(self, False)
        
        label_width = 75
        self.mainwin = mainwin
        self.user = None
        self.label = gtk.Label(label)
        self.caption = label
        
        self.user_pic = gtk.Button()
        self.user_pic.set_size_request(60, 60)
        pic_box = gtk.VBox(False)
        pic_box.pack_start(self.user_pic, False, False, 10)
        
        self.screen_name = gtk.Label()
        self.screen_name.set_alignment(0, 0.5)
        self.tweets_count = gtk.Label()
        self.tweets_count.set_alignment(0, 0.5)
        self.tweets_count.set_padding(8, 0)
        self.following_count = gtk.Label()
        self.following_count.set_alignment(0, 0.5)
        self.following_count.set_padding(8, 0)
        self.followers_count = gtk.Label()
        self.followers_count.set_alignment(0, 0.5)
        self.followers_count.set_padding(8, 0)
        
        info_box = gtk.VBox(False)
        info_box.pack_start(self.screen_name, False, False, 5)
        info_box.pack_start(self.tweets_count, False, False)
        info_box.pack_start(self.following_count, False, False)
        info_box.pack_start(self.followers_count, False, False)
        
        top = gtk.HBox(False)
        top.pack_start(pic_box, False, False, 10)
        top.pack_start(info_box, False, False, 5)
        
        self.real_name = gtk.Entry()
        self.real_name.set_max_length(20)
        name_lbl = gtk.Label('Nombre')
        name_lbl.set_size_request(label_width, -1)
        name_box = gtk.HBox(False)
        name_box.pack_start(name_lbl, False, False, 2)
        name_box.pack_start(self.real_name, True, True, 5)
        
        self.location = gtk.Entry()
        self.location.set_max_length(30)
        loc_lbl = gtk.Label('Ubicacion')
        loc_lbl.set_size_request(label_width, -1)
        loc_box = gtk.HBox(False)
        loc_box.pack_start(loc_lbl, False, False, 2)
        loc_box.pack_start(self.location, True, True, 5)
        
        self.url = gtk.Entry()
        self.url.set_max_length(100)
        url_lbl = gtk.Label('URL')
        url_lbl.set_size_request(label_width, -1)
        url_box = gtk.HBox(False)
        url_box.pack_start(url_lbl, False, False, 2)
        url_box.pack_start(self.url, True, True, 5)
        
        self.bio = gtk.TextView()
        self.bio.set_wrap_mode(gtk.WRAP_WORD)
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scrollwin.set_shadow_type(gtk.SHADOW_IN)
        scrollwin.set_size_request(-1, 80)
        scrollwin.add(self.bio)
        bio_lbl = gtk.Label('Bio')
        bio_lbl.set_size_request(label_width, -1)
        bio_box = gtk.HBox(False)
        bio_box.pack_start(bio_lbl, False, False, 2)
        bio_box.pack_start(scrollwin, True, True, 5)
        
        form = gtk.VBox(False)
        form.pack_start(name_box, False, False, 4)
        form.pack_start(loc_box, False, False, 4)
        form.pack_start(url_box, False, False, 4)
        form.pack_start(bio_box, False, False, 4)
        
        self.submit = gtk.Button('Guardar')
        submit_box = gtk.Alignment(1.0, 0.5)
        submit_box.set_property('right-padding', 5)
        submit_box.add(self.submit)
        
        self.pack_start(top, False, False)
        self.pack_start(form, False, False)
        self.pack_start(submit_box, False, False)
        
        self.submit.connect('clicked', self.save_user_profile)
        
    def update(self, profile):
        self.user = profile['screen_name']
        pix = self.mainwin.get_user_avatar(self.user, profile['profile_image_url'])
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        self.user_pic.set_image(avatar)
        del pix
        self.screen_name.set_markup('<b>@%s</b>' % profile['screen_name'])
        self.tweets_count.set_markup('<span size="9000">%i Tweets</span>' % profile['statuses_count'])
        self.following_count.set_markup('<span size="9000">%i Following</span>' % profile['friends_count'])
        self.followers_count.set_markup('<span size="9000">%i Followers</span>' % profile['followers_count'])
        self.real_name.set_text(profile['name'])
        if profile['location']: self.location.set_text(profile['location'])
        if profile['url']: self.url.set_text(profile['url'])
        buffer = self.bio.get_buffer()
        if profile['description']: buffer.set_text(profile['description'])
        self.unlock()
        
    def update_user_pic(self, user, pic):
        if self.user != user: return
        pix = util.load_avatar(self.mainwin.imgdir, pic, True)
        self.user_pic.set_image(pix)
        
    def save_user_profile(self, widget):
        self.lock()
        name = self.real_name.get_text()
        location = self.location.get_text()
        url = self.url.get_text()
        buffer = self.bio.get_buffer()
        bounds = buffer.get_bounds()
        bio = buffer.get_text(bounds[0], bounds[1])[:160]
        self.mainwin.request_update_profile(name, url, bio, location)
        
    def lock(self):
        self.real_name.set_sensitive(False)
        self.location.set_sensitive(False)
        self.url.set_sensitive(False)
        self.bio.set_sensitive(False)
        self.submit.set_label('Guardando...')
        self.submit.set_sensitive(False)
    
    def unlock(self):
        self.real_name.set_sensitive(True)
        self.location.set_sensitive(True)
        self.url.set_sensitive(True)
        self.bio.set_sensitive(True)
        self.submit.set_label('Guardar')
        self.submit.set_sensitive(True)
        
    def update_wrap(self, w):
        pass
