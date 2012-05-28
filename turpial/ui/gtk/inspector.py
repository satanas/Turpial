import gtk
import webkit

class TurpialInspector ():
    def __init__ (self, inspector):
        self.webview = webkit.WebView()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.webview)
        scroll.show_all()

        self.window = gtk.Window()
        self.window.add(scroll)
        self.window.set_default_size(600, 480)
        self.window.set_title("Turpial Inspector")
        self.window.connect("delete-event", self.on_delete_event)

        inspector.set_property("javascript-profiling-enabled", True)
        inspector.connect("inspect-web-view", self.on_inspect_web_view)
        inspector.connect("show-window", self.on_show_window)
        inspector.connect("close-window", self.on_close_window)
        inspector.connect("finished", self.on_finished)

    def __del__ (self):
        self.window.destory()

    def on_delete_event (self, widget, event):
        self.window.hide()
        return True

    def on_inspect_web_view (self, inspector, web_view):
        return self.webview

    def on_show_window (self, inspector):
        self.window.show_all()
        self.window.present()
        return True

    def on_close_window (self, inspector):
        self.window.hide()
        return True

    def on_finished (self, inspector):
        self.window.hide()
