#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Controlador de Turpial'''

#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import os
import sys
import base64
import logging
import getpass
from optparse import OptionParser

from turpial.api.servicesapi import HTTPServices
from turpial.api.turpialapi import TurpialAPI
from turpial.config import ConfigHandler, ConfigApp, ConfigProtocol, PROTOCOLS
from turpial.ui.cmd.main import Main as _CMD

try:
    import ctypes
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, 'turpial', 0, 0)
except ImportError:
    pass

INTERFACES = ['cmd']
try:
    from turpial.ui.gtk.main import Main as _GTK
    UI_GTK = True
    INTERFACES.append('gtk')
    INTERFACES.append('gtk+')
except ImportError:
    UI_GTK = False

class Turpial:
    '''Inicio de Turpial'''
    def __init__(self):
        ui_avail = '('
        for ui in INTERFACES:
            ui_avail += ui + '|'
        ui_avail = ui_avail[:-1] + ')'
        default_ui = INTERFACES[1] if len(INTERFACES) > 1 else ''
        
        parser = OptionParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='show debug info in shell during execution', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='select interface to use %s' % ui_avail, default=default_ui)
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='clean all bytecodes', default=False)
        parser.add_option('-s', '--save-credentials', dest='save', action='store_true',
            help='save user credentials', default=False)
        parser.add_option('--version', dest='version', action='store_true',
            help='show the version of Turpial and exit', default=False)
        parser.add_option('--test', dest='test', action='store_true',
            help='only load timeline and friends', default=False)
        parser.add_option('--no-sound', dest='no_sound', action='store_true',
            help='disable the sounds module', default=False)
        parser.add_option('--no-notif', dest='no_notif', action='store_true',
            help='disable the notifications module', default=False)
        
        (options, args) = parser.parse_args()
        
        self.config = None
        self.global_cfg = ConfigApp()
        self.protocol_cfg = {}
        self.profile = None
        self.testmode = options.test
        self.interface = options.interface
        self.no_sound = options.no_sound
        self.no_notif = options.no_notif
        self.httpserv = None
        self.api = None
        self.version = self.global_cfg.read('App', 'version')
        
        for p in PROTOCOLS:
            self.protocol_cfg[p] = ConfigProtocol(p)
        
        if options.debug or options.clean: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        if options.clean:
            self.__clean()
            sys.exit(0)
            
        if options.version:
            print "Turpial v%s" % self.version
            print "Python v%X" % sys.hexversion
            sys.exit(0)
            
        if options.save:
            try:
                self.__save_credentials()
            except KeyboardInterrupt:
                self.log.debug('Interceptado Keyboard Interrupt')
            sys.exit(0)
            
        self.interface = options.interface
        if options.interface == 'gtk+' and ('gtk+' in INTERFACES):
            self.ui = _GTK(self, extend=True)
        elif options.interface == 'gtk' and ('gtk' in INTERFACES):
            self.ui = _GTK(self)
        elif options.interface == 'cmd' and ('cmd' in INTERFACES):
            self.ui = _CMD(self, args)
        else:
            print 'No existe una interfaz válida. Las interfaces válidas son: %s' % INTERFACES
            print 'Saliendo...'
            sys.exit(-1)
        
        self.httpserv = HTTPServices()
        self.api = TurpialAPI()
        
        self.log.debug('Iniciando Turpial v%s' % self.version)
        if self.interface  != 'cmd':
            self.httpserv.start()
        self.api.start()
        self.api.change_api_url(self.global_cfg.read('Proxy', 'url'))
        
        if self.testmode:
            self.log.debug('Modo Pruebas Activado')
            
        self.ui.show_login()
        try:
            self.ui.main_loop()
        except KeyboardInterrupt:
            self.log.debug('Interceptado Keyboard Interrupt')
            self.ui.main_quit()
        
    def __clean(self):
        '''Limpieza de ficheros .pyc y .pyo'''
        self.log.debug("Limpiando la casa...")
        path = os.path.join(os.path.dirname(__file__))
        i = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                path = os.path.join(root, f)
                if path.endswith('.pyc') or path.endswith('.pyo'): 
                    self.log.debug("Borrado %s" % path)
                    os.remove(path)
            
    def __save_credentials(self):
        print "This assistant will allow you store your credentials"
        print "Available protocols"
        print "==================="
        for i in range(len(PROTOCOLS)):
            print "%d - %s" % (i, PROTOCOLS[i])
        
        while 1:
            protocol = int(raw_input("Select protocol: "))
            if protocol <= len(PROTOCOLS):
                break
            else:
                print "Invalid protocol, please try again"
        
        user, passwd, rem = self.get_remembered(protocol)
        if user != '' and passwd != '':
            delete = raw_input("Delete your current credentials (%s)? [Y/n/q]: " %
                user)
            if delete == '' or delete.lower() == 'y':
                self.remember(pro=protocol, rem=False)
                return
            elif delete.lower() == 'q':
                return
        
        user = raw_input("User: ")
        while 1:
            passwd = getpass.getpass("Password: ")
            confirm = getpass.getpass("Retype password: ")
            if passwd == confirm:
                break
            else:
                print
                print "Password mismatch, please try again"
        self.remember(user, passwd, protocol, True)
        print "Credentials saved successfully"
        
    def __validate_credentials(self, val, key, secret, protocol):
        '''Chequeo de credenciales'''
        if val.type == 'error':
            self.ui.cancel_login(val.errmsg)
        elif val.type == 'profile':
            self.profile = val.items
            self.config = ConfigHandler(self.profile.username, protocol)
            self.config.initialize()
            
            self.current_protocol = protocol
            self.httpserv.update_img_dir(self.config.imgdir)
            self.httpserv.set_credentials(self.profile.username, 
                self.profile.password, self.api.protocol.http)
            
            self.__signin_done(key, secret, val)
    
    def __done_follow(self, response):
        user = response.items[1]
        follow = response.items[2]
        
        if response.type == 'error':
            msg = response.errmsg % user
            self.ui.following_error(msg, follow)
        elif response.type == 'mixed':
            self.profile = response.items[0]
            self.ui.update_user_profile(self.profile)
            self.ui.update_follow(user, follow)
        
    def __direct_done(self, status):
        self.ui.tweet_done(status)
        
    def __tweet_done(self, status):
        if status:
            self.profile.statuses_count += 1
            self.ui.update_user_profile(self.profile)
        self.ui.tweet_done(status)
        
    def __signin_done(self, key, secret, resp_profile):
        '''Inicio de sesion finalizado'''
        
        # TODO: Llenar con el resto de listas
        self.lists = {
            'timeline': MicroBloggingList('timeline', '', _('Timeline'),
                _('tweet'), _('tweets')),
            'replies': MicroBloggingList('replies', '', _('Replies'),
                _('mention'), _('mentions')),
            'directs': MicroBloggingList('directs', '', _('Directs'),
                _('direct'), _('directs')),
            'sent': MicroBloggingList('sent', '', _('My Tweets'), 
                _('tweet'), _('tweets')),
        }
        
        if self.interface  != 'cmd':
            plists = self.api.get_lists()
            for ls in plists:
                self.lists[str(ls.id)] = MicroBloggingList(str(ls.id), ls.user, 
                    ls.name, _('tweet'), _('tweets'))
        
        # Evita que la aplicación reviente si se borra una lista por fuera
        try:
            column1 = self.lists[self.config.read('Columns', 'column1')]
        except KeyError:
            self.log.debug('La lista %s no existe. Se carga el Timeline' % 
                self.config.read('Columns', 'column1'))
            column1 = self.lists['timeline']
        
        try:
            column2 = self.lists[self.config.read('Columns', 'column2')]
        except KeyError:
            self.log.debug('La lista %s no existe. Se carga el Timeline' % 
                self.config.read('Columns', 'column2'))
            column2 = self.lists['timeline']
            
        try:
            column3 = self.lists[self.config.read('Columns', 'column3')]
        except KeyError:
            self.log.debug('La lista %s no existe. Se carga el Timeline' % 
                self.config.read('Columns', 'column3'))
            column3 = self.lists['timeline']
            
        self.viewed_cols = [column1, column2, column3]
        
        self.api.protocol.muted_users = self.config.load_muted_list()
        self.api.protocol.filtered_terms = self.config.load_filtered_list()
        self.ui.set_lists(self.lists, self.viewed_cols)
        self.ui.show_main(self.config, self.global_cfg, resp_profile)
        
        if self.interface  == 'cmd':
            return
        
        self._update_column1()
        if self.testmode:
            self._update_rate_limits()
            self._update_friends()
            return
        self._update_column2()
        self._update_column3()
        self._update_rate_limits()
        self._update_favorites()
        self._update_friends()
        
    def _update_column1(self):
        '''Actualizar columna 1'''
        self.ui.start_updating_column1()
        count = int(self.config.read('General', 'num-tweets'))
        column = self.viewed_cols[0]
        self.api.update_column(self.ui.update_column1, count, column)
        
    def _update_column2(self):
        '''Actualizar columna 2'''
        self.ui.start_updating_column2()
        count = int(self.config.read('General', 'num-tweets'))
        column = self.viewed_cols[1]
        self.api.update_column(self.ui.update_column2, count, column)
        
    def _update_column3(self):
        '''Actualizar columna 3'''
        self.ui.start_updating_column3()
        count = int(self.config.read('General', 'num-tweets'))
        column = self.viewed_cols[2]
        self.api.update_column(self.ui.update_column3, count, column)
        
    def _update_favorites(self):
        '''Actualizar favoritos'''
        self.api.update_favorites(self.ui.update_favorites)
    
    def _update_rate_limits(self):
        self.api.update_rate_limits(self.ui.update_rate_limits)
        
    def _update_friends(self):
        '''Actualizar amigos'''
        self.api.get_friends()
    
    def get_remembered(self, index):
        protocol = PROTOCOLS[index]
        us = self.protocol_cfg[protocol].read('Login', 'username')
        pw = self.protocol_cfg[protocol].read('Login', 'password')
        try:
            if us != '' and pw != '':
                a = base64.b64decode(pw)
                b = a[1:-1]
                c = base64.b32decode(b)
                d = c[1:-1]
                e = base64.b16decode(d)
                pwd = e[0:len(us)]+ e[len(us):]
                return us, pwd, True
            else:
                return us, pw, False
        except TypeError:
            self.protocol_cfg[protocol].write('Login', 'username','')
            self.protocol_cfg[protocol].write('Login', 'password','')
            return '', '', False
        
    def remember(self, us='', pw='', pro=0, rem=False):
        protocol = PROTOCOLS[pro]
        if not rem:
            self.protocol_cfg[protocol].write('Login', 'username', '')
            self.protocol_cfg[protocol].write('Login', 'password', '')
            return
            
        a = base64.b16encode(pw)
        b = us[0] + a + ('%s' % us[-1])
        c = base64.b32encode(b)
        d = ('%s' % us[-1]) + c + us[0]
        e = base64.b64encode(d)
        pwd = e[0:len(us)]+ e[len(us):]
        
        self.protocol_cfg[protocol].write('Login', 'username', us)
        self.protocol_cfg[protocol].write('Login', 'password', pwd)
    
    def signin(self, username, password, protocol):
        config = ConfigHandler(username, protocol)
        config.initialize_failsafe()
        auth = config.read_section('Auth')
        self.api.auth(username, password, auth, protocol,
            self.__validate_credentials)
        
    def signout(self):
        '''Finalizar sesion'''
        self.save_muted_list()
        self.save_filtered_list()
        self.log.debug('Desconectando')
        if self.httpserv and self.interface  != 'cmd':
            self.httpserv.quit()
            self.httpserv.join(0)
        if self.api: 
            self.api.quit()
            if self.interface  != 'cmd':
                self.api.join(0)
        sys.exit(0)
    
    def update_status(self, text, reply_id=None):
        if text.startswith('D '):
            self.api.update_status(text, reply_id, self.__direct_done)
        else:
            self.api.update_status(text, reply_id, self.__tweet_done)
        
    def destroy_status(self, id):
        self.api.destroy_status(id, self.ui.after_destroy_status)
        
    def set_favorite(self, id):
        self.api.set_favorite(id, self.ui.tweet_changed)
        
    def unset_favorite(self, id):
        self.api.unset_favorite(id, self.ui.tweet_changed)
    
    def repeat(self, id):
        self.api.repeat(id, self.__tweet_done)
    
    def follow(self, user):
        self.api.follow(user, self.__done_follow)
        
    def unfollow(self, user):
        self.api.unfollow(user, self.__done_follow)
        
    def update_profile(self, new_name, new_url, new_bio, new_location):
        self.api.update_profile(new_name, new_url, new_bio, new_location,
            self.ui.update_user_profile)
    
    def in_reply_to(self, id):
        self.api.in_reply_to(id, self.ui.update_in_reply_to)
        
    def get_conversation(self, id):
        self.api.get_conversation(id, self.ui.update_conversation)
    
    def mute(self, users):
        self.api.mute(users, self.ui.tweet_changed)

    def filter_term(self, term):
        self.api.filter_term(term, self.ui.tweet_changed)
    
    def short_url(self, text, callback):
        service = self.config.read('Services', 'shorten-url')
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.httpserv.download_pic(user, pic_url, callback)
        
    def upload_pic(self, path, message, callback):
        service = self.config.read('Services', 'upload-pic')
        self.httpserv.upload_pic(service, path, message, callback)
        
    def search(self, query):
        self.ui.start_search()
        self.api.search(query, self.ui.update_search)
        
    def get_popup_info(self, tweet_id, user):
        if self.api.is_marked_to_fav(tweet_id):
            return {'marking_fav': True}
        elif self.api.is_marked_to_unfav(tweet_id):
            return {'unmarking_fav': True}
        elif self.api.is_marked_to_del(tweet_id):
            return {'deleting': True}
            
        rtn = {}
        if self.api.friends_loaded():
            rtn['friend'] = self.api.is_friend(user)

        rtn['fav'] = self.api.is_fav(tweet_id)
        
        return rtn
        
    def save_config(self, config, update):
        self.config.save(config)
        if update:
            self.ui.update_config(self.config)
            
    def save_global_config(self, config):
        self.global_cfg.save(config)
        
    def save_muted_list(self):
        if self.config:
            self.config.save_muted_list(self.api.protocol.muted_users)
        
    def get_muted_list(self):
        return self.api.get_muted_list()
        
    def save_filtered_list(self):
        if self.config:
            self.config.save_filtered_list(self.api.protocol.filtered_terms)
        
    def get_filtered_list(self):
        return self.api.get_filtered_list()

    def destroy_direct(self, id):
        self.api.destroy_direct(id, self.ui.after_destroy_direct)
        
    def get_friends(self):
        return self.api.get_single_friends_list()
        
    def get_hashtags_url(self):
        return self.api.protocol.tags_url
        
    def get_groups_url(self):
        return self.api.protocol.groups_url
        
    # FIXME: Debería pasarse como parámetro el protocolo
    def get_profiles_url(self):
        return self.api.protocol.profiles_url
        
    def get_viewed_columns(self):
        return self.viewed_cols
        
    def change_column(self, index, new_id):
        print 'change_column', self.lists.keys(), index, new_id
        if self.lists.has_key(new_id):
            self.viewed_cols[index] = self.lists[new_id]
            if index == 0:
                self.ui.home.timeline.clear()
                self._update_column1()
            elif index == 1:
                self.ui.home.replies.clear()
                self._update_column2()
            elif index == 2:
                self.ui.home.direct.clear()
                self._update_column3()
        else:
            self.ui.set_column_item(index, reset=True)
            self.log.debug('Error: la columna %s no existe' % new_id)
            
    def is_friend(self, user):
        return self.api.is_friend(user)
        
class MicroBloggingList:
    ''' Lista de los diferentes protocolos '''
    def __init__(self, id, user, title, sunit, punit):
        self.id = id
        self.user = user
        self.title = title
        self.single_unit = sunit
        self.plural_unit = punit
    
if __name__ == '__main__':
    t = Turpial()
