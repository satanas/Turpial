# -*- coding: utf-8 -*-

# Lazy factory for images in GTK3 Turpial

class ImagesFactory:
    def __init__(self, base):
        self.base = base
        self._unknown_avatar = None
        self._reposted_mark = None
        self._verified_mark = None
        self._protected_mark = None

    def unknown_avatar(self, pixbuf=True):
        if not self._unknown_avatar:
            self._unknown_avatar = self.base.load_image('unknown.png', pixbuf)
        return self._unknown_avatar

    def reposted_mark(self):
        if not self._reposted_mark:
            self._reposted_mark = self.base.load_image('mark-reposted.png', True)
        return self._reposted_mark

    def protected_mark(self):
        if not self._protected_mark:
            self._protected_mark = self.base.load_image('mark-protected.png', True)
        return self._protected_mark

    def verified_mark(self):
        if not self._verified_mark:
            self._verified_mark = self.base.load_image('mark-verified.png', True)
        return self._verified_mark
