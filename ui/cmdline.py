# -*- coding: utf-8 -*-

# Vista en modo texto para Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import cmd
import util
import getpass
import logging
import datetime

log = logging.getLogger('Cmdline')
INTRO = [
    'Bienvenido a Turpial, un cliente Twitter para GNU/Linux.', 
    'Escriba "help" para obtener una lista de los comandos disponibles.',
    'Escriba "help <comando>" para obtener una ayuda detallada de un comando'
]
class Main(cmd.Cmd):
    def __init__(self, controller):
        cmd.Cmd.__init__(self)
        self.controller = controller
        self.prompt = 'turpial> '
        self.intro = '\n'.join(INTRO)
        
    def main_loop(self):
        pass
        
    def update_timeline(self, tweets):
        pass
        
    def update_rate_limits(self, rates):
        pass
        
    def default(self, line):
        print '\n'.join(['Comando no encontrado.', INTRO[1], INTRO[2]])
        
    def do_show(self, arg):
        if arg == 'tweets':
            self.show_tweets(self.controller.get_timeline())
        elif arg == 'replies':
            self.show_tweets(self.controller.replies)
        elif arg == 'directs':
            self.show_tweets(self.controller.directs)
        elif arg == 'directs_sent':
            self.show_tweets(self.controller.directs_sent)
        elif arg == 'favs':
            self.show_tweets(self.controller.favs)
        elif arg == 'rates':
            self.show_rate_limits()
        elif arg == 'trends':
            self.show_trends(self.controller.get_trends())
        elif arg == 'profile':
            self.show_profile([self.controller.profile])
        elif arg == 'following':
            self.show_following(self.controller.get_following())
        elif arg == 'followers':
            self.show_followers(self.controller.get_followers())
        else:
            self.default('')
    
    def do_search(self, args):
        args = args.split()
        if len(args) < 2: 
            self.help_search()
            return
        stype = args[0]
        query = args[1]
        
        if stype == 'people':
            self.show_profile(self.controller.search_people(query))
        
    def do_tweet(self, status):
        if not self.validate_message(status):
            print 'Tu estado NO fue actualizado.'
            return
        
        self.controller.update_status(status)
        
    def do_delete(self, number):
        twid = self.get_tweet_id(number)
        if twid is None:
            print 'No se puede localizar el mensaje seleccionado'
            print 'El mensaje NO fue borrado.'
            return
        self.controller.destroy_status(twid)
        
    def do_fav(self, number):
        twid = self.get_tweet_id(number)
        if twid is None:
            print 'No se puede localizar el mensaje seleccionado'
            print 'El mensaje NO fue marcado.'
            return
        self.controller.set_favorite(twid)
        
    def do_unfav(self, number):
        twid = self.get_tweet_id(number)
        if twid is None:
            print 'No se puede localizar el mensaje seleccionado'
            print 'El mensaje NO fue desmarcado.'
            return
        self.controller.unset_favorite(twid)
        
    def do_direct(self, line):
        if len(line.split()) < 2: 
            self.help_direct()
            return
        user = line.split()[0]
        message = line.replace(user + ' ', '')
        if not self.validate_message(message):
            print 'NO se envio ningun mensaje.'
            return
        self.controller.send_direct(user, message)
        
    def do_update(self, args):
        if len(args.split()) < 2: 
            self.help_update()
            return
        field = args.split()[0]
        value = args.replace(field + ' ', '')
        
        if field == 'bio':
            if not self.validate_message(value, 160):
                print 'NO se actualizo la bio.'
                return
            self.controller.update_profile(new_bio=value)
        elif field == 'location':
            if not self.validate_message(value, 30):
                print 'NO se actualizo la ubicacion.'
                return
            self.controller.update_profile(new_location=value)
        elif field == 'url':
            if not self.validate_message(value, 100):
                print 'NO se actualizo la URL.'
                return
            self.controller.update_profile(new_url=value)
        elif field == 'name':
            if not self.validate_message(value, 20):
                print 'NO se actualizo el nombre.'
                return
            self.controller.update_profile(new_name=value)
        
    def do_mute(self, user):
        self.controller.mute(user)
        
    def do_unmute(self, user):
        self.controller.unmute(user)
        
    def do_follow(self, user):
        self.controller.follow(user)
        
    def do_unfollow(self, user):
        self.controller.unfollow(user)
        
    def do_EOF(self, line):
        return self.do_exit('')
        
    def do_exit(self, line):
        print
        log.debug('Desconectando')
        self.controller.signout()
        log.debug('Adios')
        return True
        
    def help_show(self):
        print '\n'.join(['Muestra los distintos mensajes del usuario',
            'show <arg>',
            '  <arg>: Lo que se desea ver. Valores posibles: tweets, ' \
            'replies, directs, favs, rates, trends, profile, following, ' \
            'followers',
        ])
        
    def help_search(self):
        print '\n'.join(['Ejecuta una busqueda en Twitter',
            'search <type> <query>',
            '  <type>: Tipo de busqueda a realizar. Valores ' \
                'posibles: people',
            '  <query>: La cadena que se desea buscar'
        ])
        
    def help_direct(self):
        print '\n'.join(['Envia un mensaje directo a un usuario',
            'direct <user> <message>',
            '  <user>: Nombre del usuario. Ej: pedroperez',
            '  <message>: Mensaje que se desea enviar'
        ])
        
    def help_update(self):
        print '\n'.join(['Actualiza datos del usuario',
            'update <field> <value>',
            '  <field>: Campo que se desea actualizar. Valores ' \
                'posibles: bio, location, url, name',
            '  <value>: El nuevo valor para el campo seleccionado'
        ])
    
    def help_delete(self):
        print '\n'.join(['Borra un estado (tweet)',
            'delete <num>',
            '  <num>: Numero en pantalla del estado (tweet) que desea borrar',
        ])
        
    def help_fav(self):
        print '\n'.join(['Marca un estado (tweet) como favorito',
            'fav <num>',
            '  <num>: Numero en pantalla del estado (tweet) que desea marcar',
        ])
        
    def help_unfav(self):
        print '\n'.join(['Desmarca un estado (tweet) de los favoritos',
            'unfav <num>',
            '  <num>: Numero en pantalla del estado (tweet) que desea desmarcar',
        ])
        
    def help_tweet(self):
        print '\n'.join(['Actualiza el estado del usuario',
            'tweet <message>',
            '  <message>: Mensaje que desea postear',
        ])
        
    def help_follow(self):
        print '\n'.join(['Seguir a una persona',
            'follow <user>',
            '  <user>: Persona a la que desea seguir',
        ])
        
    def help_unfollow(self):
        print '\n'.join(['Dejar de seguir a una persona',
            'unfollow <user>',
            '  <user>: Persona que ya no se desea seguir',
        ])
        
    def help_mute(self):
        print '\n'.join(['Silencia los mensajes de una persona sin bloquearla',
            'mute <user>',
            '  <user>: Persona a la que se desea silenciar',
        ])
        
    def help_unmute(self):
        print '\n'.join(['Visualiza los mensajes de una persona previamente silenciada',
            'unmute <user>',
            '  <user>: Persona cuyos mensajes se desean leer de nuevo',
        ])
        
    def help_help(self):
        print 'Muestra la ayuda'
        
    def help_exit(self):
        print 'Salir de Turpial'
    
    def help_EOF(self):
        print 'Salir de Turpial'
        
    def get_tweet_id(self, num):
        if num == '': return None
        
        num = int(num) - 1
        arr = self.controller.tweets[:]
        arr.reverse()
        if (num < 1) or (num > len(arr)): return None
        
        return arr[num]['id']
        
    def validate_message(self, text, limit=140):
        if text == '':
            print 'Debes escribir algun mensaje.'
            return False
        
        if len(text) > 160:
            print 'Tu mensaje tiene mas de 160 caracteres y Twitter ' \
                'lo rechazara. Intenta acortar algunas URLs antes ' \
                'de postear.'
            return False
        
        if len(text) > limit:
            resp = raw_input('El mensaje supera los 140 caracteres y ' \
            'Twitter lo truncara. ¿Deseas continuar? [Y/n]')
            if resp.lower() == 'n':
                return False
        return True
        
    def show_main(self):
        self.cmdloop()
        
    def show_login(self):
        usuario = raw_input('Username: ')
        password = getpass.unix_getpass()
        log.debug('Autenticando')
        self.controller.signin(usuario, password)
    
    def cancel_login(self, error):
        print error
        self.show_login()
        
    def show_tweets(self, tweets):
        count = 1
        arr_tweets = tweets[:]
        arr_tweets.reverse()
        
        for tweet in arr_tweets:
            timestamp = util.get_timestamp(tweet)
            
            if tweet.has_key('user'):
                user = tweet['user']['screen_name']
            else:
                user = tweet['sender']['screen_name']
            
            if tweet.has_key('source'):
                client = util.detect_client(tweet['source'])
                header = "%d. @%s - %s desde %s" % (count, user, timestamp, client)
            else:
                header = "%d. @%s - %s" % (count, user, timestamp)
            
            print header
            print '-' * len(header)
            print tweet['text']
            print
            count += 1
            
        self.show_rate_limits()
        
    def show_rate_limits(self):
        rates = self.controller.update_rate_limits()
        print util.get_rates(rates)
    
    def show_trends(self, trends):
        topten = ''
        for t in trends['trends']:
            topten += t['name'] + '  '
        print topten
            
    def show_profile(self, people):
        for p in people:
            protected = ''
            following = ''
            if p['protected']: protected = '<protected>'
            if p['following']: protected = '<following>'
            
            header = "@%s (%s) %s %s" % (p['screen_name'], p['name'], 
                following, protected)
            print header
            print '-' * len(header)
            print "URL: %s" % p['url']
            print "Location: %s" % p ['location']
            print "Bio: %s" % p ['description']
            if p.has_key('status'): print "Last: %s\n" % p['status']['text']
        
    def show_following(self, people):
        total = len(people)
        self.show_profile(people)
        if total > 1: suffix = 'personas' 
        else: suffix = 'persona'
        print "Estas siguiendo a %d %s" % (total, suffix)
        
    def show_followers(self, people):
        total = len(people)
        self.show_profile(people)
        if total > 1: suffix = 'personas' 
        else: suffix = 'persona'
        print "Te siguen %d %s" % (total, suffix)

