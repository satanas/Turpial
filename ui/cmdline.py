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
            self.show_tweets(self.controller.tweets)
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
            self.show_people(self.controller.search_people(query))
        
    def do_tweet(self, status):
        if status == '':
            print 'Debes escribir algun mensaje para postear.'
            print 'Tu estado NO fue actualizado.'
            return
        
        if len(status) > 160:
            print 'Tu mensaje tiene mas de 160 caracteres y Twitter lo' \
                'rechazara. Intenta acortar algunas URLs antes de postear.'
            print 'Tu estado NO fue actualizado.'
            return
        
        if len(status) > 140:
            resp = raw_input('El mensaje supera los 140 caracteres, ¿Deseas ' \
                'cortarlo? [Y/n]')
            if resp.lower() == 'n':
                print 'Tu estado NO fue actualizado'
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
        if len(line) < 2: 
            self.help_direct()
            return
        user = line.split()[0]
        message = line.replace(user + ' ', '')
        self.controller.send_direct(user, message)
        
    def do_EOF(self, line):
        return self.do_exit()
        
    def do_exit(self):
        print
        log.debug('Desconectando')
        self.controller.signout()
        log.debug('Adios')
        return True
        
    def help_show(self):
        print '\n'.join(['Muestra los distintos mensajes del usuario',
            'show <arg>',
            '  <arg>: Lo que se desea ver. Valores posibles: tweets, ' \
            'replies, directs, favs, rates, trends',
        ])
        
    def help_search(self):
        print '\n'.join(['Ejecuta una busqueda en Twitter',
            'search <type> <query>',
            '  <type>: Tipo de busqueda a realizar. Valores posibles: people',
            '  <query>: La cadena que se desea buscar'
        ])
        
    def help_direct(self):
        print '\n'.join(['Envia un mensaje directo a un usuario',
            'direct <user> <message>',
            '  <user>: Nombre del usuario. Ej: pedroperez',
            '  <message>: Mensaje que se desea enviar'
        ])
        
    def get_tweet_id(self, num):
        if num == '': return None
        
        num = int(num) - 1
        arr = self.controller.tweets[:]
        arr.reverse()
        if (num < 1) or (num > len(arr)): return None
        
        return arr[num]['id']
        
    def get_timestamp(self, tweet):
        return tweet['created_at'][0:19]
        #print ttime, type(ttime)
        #t = ttime[0:19] + ttime[25:]
        #a = time.strptime(t, '%a %b %d %H:%M:%S %Y')
        a = time.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        sec = time.mktime(a) - time.timezone
        return time.strftime('%b %d, %I:%M %P', sec)
        
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
            timestamp = self.get_timestamp(tweet)
            
            if tweet.has_key('user'):
                user = tweet['user']['screen_name']
            else:
                user = tweet['sender']['screen_name']
            
            if tweet.has_key('client'):
                client = util.detect_client(tweet['source'])
                header = "%d. @%s el %s desde %s" % (count, user, timestamp, client)
            else:
                header = "%d. @%s el %s" % (count, user, timestamp)
            
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
    
    def show_people(self, people):
        for p in people:
            if p['protected']:
                protected = '<protected>'
            else:
                protected = ''
            header = "@%s: %s (id=%s) %s" % (p['screen_name'], p['name'], p['id'], protected)
            print header
            print '-' * len(header)
            print "Location: %s" % p ['location']
            if p.has_key('status'): print "Last: %s\n" % p['status']['text']
            

