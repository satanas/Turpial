# -*- coding: utf-8 -*-

# Qt image view for Turpial

import os
import shutil

from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QMovie
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QApplication

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import Window, BarLoadIndicator

GOOGLE_SEARCH_URL = 'https://www.google.com/searchbyimage?&image_url='

try:
    import exifread
    EXIF_SUPPORT = True
except:
    EXIF_SUPPORT = False

class ImageView(Window):
    EMPTY = 0
    LOADING = 1
    LOADED = 2
    def __init__(self, base):
        Window.__init__(self, base, i18n.get('image_preview'))

        self.loader = BarLoadIndicator()
        self.source_url = None
        self.original_url = None
        self.local_file = None
        self.pixmap = None
        self.status = self.EMPTY

        self.view = QLabel()

        self.error_label = QLabel(i18n.get('error_loading_image'))
        self.error_label.setAlignment(Qt.AlignHCenter)
        self.error_label.setStyleSheet("QLabel {background-color: #ffecec;}")

        self.exif_data = QLabel()
        self.exif_data.setVisible(False)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loader)
        layout.addWidget(self.error_label)
        layout.addWidget(self.view)
        layout.addWidget(self.exif_data)

        self.setLayout(layout)
        self.__clear()

    def __clear(self):
        self.setFixedSize(350, 350)
        self.view.setMovie(None)
        self.view.setPixmap(QPixmap())
        self.menu = None
        self.source_url = None
        self.original_url = None
        self.local_file = None
        self.pixmap = None
        self.exif_data.setVisible(False)
        self.status = self.EMPTY

    def __load(self, url):
        self.local_file = url
        self.loader.setVisible(False)
        self.pixmap = self.base.load_image(url, True)
        screen_size = self.base.get_screen_size()

        if (screen_size.width() - 10 < self.pixmap.width() or screen_size.height() - 10 < self.pixmap.height()):
            width = min(self.pixmap.width(), screen_size.width())
            height = min(self.pixmap.height(), screen_size.height())
            self.pixmap = self.pixmap.scaled(QSize(screen_size.width(), screen_size.height()), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedSize(self.pixmap.width(), self.pixmap.height())

        if EXIF_SUPPORT:
            fd = open(url, 'rb')
            tags = exifread.process_file(fd)
            if tags != {}:
                data = {
                    'Camera': "%s %s" % (tags['Image Make'], tags['Image Model']),
                    'Software': '' if 'Image Software' not in tags else tags['Image Software'],
                    'Original Datetime': '' if 'EXIF DateTimeOriginal' not in tags else tags['EXIF DateTimeOriginal'],
                    'Dimensions': "%s x %s" % (tags['EXIF ExifImageWidth'], tags['EXIF ExifImageLength']),
                    'Copyright': '' if 'Image Copyright' not in tags else tags['Image Copyright'],
                    'Comment': '' if 'EXIF UserComment' not in tags else tags['EXIF UserComment']
                }
                exif_data = ''
                for key in ['Camera', 'Software', 'Original Datetime', 'Dimensions', 'Copyright', 'Comment']:
                    if exif_data != '':
                        exif_data += ' – '
                    exif_data += "%s: %s" % (key, data[key])
            else:
                exif_data = i18n.get('exif_data_not_available')
            self.exif_data.setText(exif_data)

        if url.find('.gif') > 0:
            movie = QMovie(url)
            self.view.setMovie(movie)
            movie.start()
        else:
            self.view.setPixmap(self.pixmap)
        self.view.adjustSize()
        self.status = self.LOADED
        self.show()

    def __copy_to_clipboard(self, url):
        clip = QApplication.clipboard()
        clip.setText(url)

    def __show_exif_data(self):
        self.exif_data.setVisible(True)

    def __save_image(self):
        local_extension = os.path.splitext(self.local_file)[1]
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(local_extension[1:])
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Images (*.png *.gif *.jpg *.jpeg)")
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.selectFile("Untitled%s" % os.path.splitext(self.local_file)[1])
        if (dialog.exec_() == QDialog.Accepted):
            filenames = dialog.selectedFiles()
            if len(filenames) > 0:
                filename = str(filenames[0])

                try:
                    shutil.copy(self.local_file, filename)
                except Exception, exc:
                    print exc
                    self.error_label.setText(i18n.get('error_saving_image'))
                    self.error_label.setVisible(True)

    def __popup_menu(self, point):
        self.menu = QMenu(self)

        if self.status == self.LOADED:
            save = QAction(i18n.get('save'), self)
            open_ = QAction(i18n.get('open_in_browser'), self)
            copy = QAction(i18n.get('copy_image_url'), self)
            verify_image = QAction(i18n.get('verify_image'), self)
            view_info = QAction(i18n.get('view_exif_info'), self)

            if self.source_url:
                open_.triggered.connect(lambda x: self.base.open_in_browser(self.original_url))
                copy.triggered.connect(lambda x: self.__copy_to_clipboard(self.source_url))
                verify_url = ''.join([GOOGLE_SEARCH_URL, self.source_url])
                verify_image.triggered.connect(lambda x: self.base.open_in_browser(verify_url))
            else:
                open_.setEnabled(False)
                copy.setEnabled(False)
                verify_image.setEnabled(False)

            if EXIF_SUPPORT:
                view_info.triggered.connect(lambda x: self.__show_exif_data())
            else:
                view_info.setEnabled(False)

            save.triggered.connect(lambda x: self.__save_image())
            view_info.triggered.connect(lambda x: self.__show_exif_data())

            self.menu.addAction(save)
            self.menu.addAction(open_)
            self.menu.addAction(copy)
            self.menu.addAction(verify_image)
            self.menu.addAction(view_info)
        else:
            loading = QAction(i18n.get('loading'), self)
            loading.setEnabled(False)
            self.menu.addAction(loading)

        self.menu.exec_(QCursor.pos())

    def closeEvent(self, event):
        event.ignore()
        self.__clear()
        self.hide()

    def start_loading(self, image_url=None):
        self.status = self.LOADING
        self.loader.setVisible(True)
        self.error_label.setVisible(False)
        self.show()

    def load_from_url(self, url):
        self.__load(url)

    def load_from_object(self, media):
        if media.info:
            self.source_url = media.info['source_url']
            self.original_url = media.info['original_url']
        self.__load(media.path)

    def error(self):
        self.loader.setVisible(False)
        self.error_label.setVisible(True)

