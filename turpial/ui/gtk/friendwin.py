# -*- coding: utf-8 -*-

# Diálogo para agregar amigos en Turpial
#
# Author: Wil Alvarez (aka Satanas)

import gtk
import gobject

class FriendsWin(gtk.Window):
    def __init__(self, parent, callback, friends):
        gtk.Window.__init__(self)
        
        self.updatebox = parent
        self.set_title(_('Add friend'))
        self.set_size_request(200, 250)
        self.set_transient_for(parent)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.callback = callback
        self.entry = gtk.Entry()
        
        self.model = gtk.ListStore(str)
        self.model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_justify(gtk.JUSTIFY_FILL)
        label.set_width_chars(25)
        
        align = gtk.Alignment(xalign=0.0, yalign=0.5)
        align.set_padding(0, 5, 10, 10)
        align.add(label)
        
        self.modelfilter = self.model.filter_new()
        self.modelfilter.set_visible_func(self.__filter, self.entry)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.list.set_model(self.modelfilter)
        
        self.cell_tweet = gtk.CellRendererText()
        column = gtk.TreeViewColumn('friends')
        column.set_alignment(0.0)
        column.pack_start(self.cell_tweet, True)
        column.set_attributes(self.cell_tweet, markup=0)
        self.list.append_column(column)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)
        
        hbox = gtk.HBox(False)
        hbox2 = gtk.HBox(False)
        
        if friends is not None:
            for friend in friends:
                self.model.append([friend])
            
            if len(friends) > 0:
                hbox.pack_start(self.entry, True, True, 2)
                hbox2.pack_start(scroll, True, True, 2)
                
                vbox = gtk.VBox(False)
                vbox.pack_start(hbox, False, False, 1)
                vbox.pack_start(hbox2, True, True, 1)
            elif len(friends) == 0:
                label.set_markup(
                    '<span foreground="#920d12">%s</span>' %
                    _(
                        'What? You don\'t have any friends.'
                        ' Try to go out and know some nice people'
                    )
                )
                vbox = gtk.HBox(False)
                vbox.pack_start(align, True, True, 2)
        else:
            label.set_markup(
                '<span foreground="#920d12">%s</span>' %
                _(
                    'I am still loading all of your friends.'
                    ' Try again in a few seconds'
                )
            )
            vbox = gtk.HBox(False)
            vbox.pack_start(align, True, True, 2)
        
        self.add(vbox)
        
        self.connect('key-release-event', self.__detect_shortcut)
        self.connect('delete-event', self.__close)
        self.entry.connect('changed', self.__find)
        self.list.connect('row-activated', self.__choose)
        
        self.show_all()
        self.entry.grab_focus()
        
    def __detect_shortcut(self, widget, event=None):
        keyname = gtk.gdk.keyval_name(event.keyval)
        
        if keyname.lower() == 'escape':
            self.__close(widget)
            
    def __find(self, widget):
        self.modelfilter.refilter()
        
    def __filter(self, model, iter, entry):
        user = model.get_value(iter, 0)
        if not user: return False
        
        query = entry.get_text().lower()
        user_l = user.lower()
        #user_u = user.upper()
        #return (user_l.startswith() or 
        #    user_u.startswith(entry.get_text()))
        return user_l.startswith(query)
        
    def __choose(self, treeview, path, view_column):
        iter = self.modelfilter.get_iter(path)
        user = '@' + self.modelfilter.get_value(iter, 0)
        self.callback(user)
        self.__close(treeview, None)
        
    def __close(self, widget, event=None):
        self.destroy()
        self.updatebox.set_focus(self.updatebox.update_text)
