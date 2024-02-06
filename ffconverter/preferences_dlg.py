# Copyright (C) 2023-2024 l-koehler
# Copyright (C) 2011-2016 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os

from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import (
        QDialog, QDialogButtonBox, QFileDialog, QLabel, QLineEdit,
        QRadioButton, QSpacerItem, QTabWidget, QToolButton, QWidget,
        QPlainTextEdit, QPushButton, QCheckBox, QMessageBox
        )

from ffconverter import utils
from ffconverter import config


class Preferences(QDialog):
    def __init__(self, parent=None, test = False):
        super(Preferences, self).__init__(parent)
        self.parent = parent
        self.test = test

        saveQL = QLabel('<html><b>' + self.tr('Save files') + '</b></html>')
        existQL = QLabel(self.tr('Existing files:'))
        self.exst_prefixQRB = QRadioButton(self.tr("Add '~' prefix"))
        self.exst_overwriteQRB = QRadioButton(self.tr('Overwrite'))
        exist_layout = utils.add_to_layout(
                'h', self.exst_prefixQRB, self.exst_overwriteQRB)

        defaultQL = QLabel(self.tr('Default output destination:'))
        self.defaultQLE = QLineEdit()
        self.defaultQTB = QToolButton()
        self.defaultQTB.setText('...')
        default_fol_layout = utils.add_to_layout(
                'h', self.defaultQLE, self.defaultQTB)
        nameQL = QLabel('<html><b>' + self.tr('Name files') +'</b></html>')
        prefixQL = QLabel(self.tr('Prefix:'))
        suffixQL = QLabel(self.tr('Suffix:'))
        self.prefixQLE = QLineEdit()
        self.suffixQLE = QLineEdit()
        grid = utils.add_to_grid(
                [prefixQL, self.prefixQLE],
                [suffixQL, self.suffixQLE])
        prefix_layout = utils.add_to_layout('h', grid, None)
        otherQL = QLabel('<html><b>' + self.tr('Other Settings') +'</b></html>')
        # set elements here
        commonformatsQL = QLabel(self.tr('Add "common" formats:'))
        self.commonformatsQPTE = QPlainTextEdit()
        doubleformatsQL = QLabel(self.tr('Add double-extensions:'))
        self.doubleformatsQPTE = QPlainTextEdit()

        other_grid = utils.add_to_grid(
                [commonformatsQL, doubleformatsQL],
                [self.commonformatsQPTE, self.doubleformatsQPTE])
        other_layout = utils.add_to_layout('h', other_grid, None)

        self.mobile_uiQChB = QCheckBox(self.tr("Use (smaller) mobile UI"))
        self.disable_cacheQChB = QCheckBox(self.tr("Disable using Cache"))
        self.delete_cacheQPB = QPushButton(self.tr("Delete Cache"))
        if os.name == 'nt':
            self.use_wslQChB = QCheckBox(self.tr("Windows: Use WSL for conversions"))
            other_optionsGrid = utils.add_to_grid([self.use_wslQChB],
                                                  [self.mobile_uiQChB],
                                                  [self.disable_cacheQChB, self.delete_cacheQPB])
        else:
            other_optionsGrid = utils.add_to_grid([self.mobile_uiQChB],
                                                  [self.disable_cacheQChB, self.delete_cacheQPB])

        tabwidget1_layout = utils.add_to_layout(
                'v', saveQL,
                QSpacerItem(14, 13), existQL, exist_layout,
                QSpacerItem(14, 13), defaultQL, default_fol_layout,
                QSpacerItem(13, 13), nameQL,
                QSpacerItem(14, 13), prefix_layout,
                QSpacerItem(14, 13), otherQL,
                QSpacerItem(14, 13), other_layout,
                QSpacerItem(14, 13), other_optionsGrid,
                )

        ffmpegQL = QLabel('<html><b>FFmpeg</b></html>')
        ffmpeg_pathQL= QLabel(self.tr('Path to executable:'))
        self.ffmpegpathQLE = QLineEdit()

        default_cmd_ffmpegQL = QLabel(self.tr('Default command:'))
        self.ffmpegcmdQLE = QLineEdit()

        vidcodecsQL = QLabel(
                '<html><b>' + self.tr('Video codecs') +'</b></html>')
        self.vidcodecsQPTE = QPlainTextEdit()
        audcodecsQL = QLabel(
                '<html><b>' + self.tr('Audio codecs') +'</b></html>')
        self.audcodecsQPTE = QPlainTextEdit()
        extraformatsffmpegQL = QLabel(
                '<html><b>' + self.tr('Extra formats') +'</b></html>')
        self.extraformatsffmpegQPTE = QPlainTextEdit()

        gridlayout = utils.add_to_grid(
                [vidcodecsQL, audcodecsQL, extraformatsffmpegQL],
                [self.vidcodecsQPTE, self.audcodecsQPTE,
                 self.extraformatsffmpegQPTE]
                )

        defvidcodecsQPB = QPushButton(self.tr("Default video codecs"))
        defaudcodecsQPB = QPushButton(self.tr("Default audio codecs"))

        hlayout1 = utils.add_to_layout(
                'h', None, defvidcodecsQPB, defaudcodecsQPB)

        tabwidget2_layout = utils.add_to_layout(
                'v', ffmpegQL, QSpacerItem(14, 13), ffmpeg_pathQL,
                self.ffmpegpathQLE, default_cmd_ffmpegQL, self.ffmpegcmdQLE,
                QSpacerItem(20, 20), gridlayout, hlayout1, None
                )

        imagemagickQL = QLabel('<html><b>ImageMagick (convert)</b></html>')
        default_cmd_imageQL = QLabel(self.tr('Default options:'))
        self.imagecmdQLE = QLineEdit()

        extraformatsimageQL = QLabel(
                '<html><b>' + self.tr('Extra formats') +'</b></html>')
        self.extraformatsimageQPTE = QPlainTextEdit()

        hlayout2 = utils.add_to_layout('h',
                self.extraformatsimageQPTE, QSpacerItem(220,20))

        tabwidget3_layout = utils.add_to_layout(
                'v', imagemagickQL,
                QSpacerItem(14,13), default_cmd_imageQL, self.imagecmdQLE,
                QSpacerItem(20,20), extraformatsimageQL, hlayout2, None
                )

        extraformatsdocumentQL = QLabel(
                '<html><b>' + self.tr('Extra formats') +'</b></html>')
        self.extraformatsdocumentQPTE = QPlainTextEdit()

        hlayout3 = utils.add_to_layout('h',
                self.extraformatsdocumentQPTE, QSpacerItem(220,20))

        tabwidget4_layout = utils.add_to_layout(
                'v', extraformatsdocumentQL, hlayout3, None)

        extraformatsmarkdownQL = QLabel(
                '<html><b>' + self.tr('Extra formats') +'</b></html>')
        self.extraformatsmarkdownQPTE = QPlainTextEdit()

        hlayout4 = utils.add_to_layout('h',
                self.extraformatsmarkdownQPTE, QSpacerItem(220,20))

        tabwidget5_layout = utils.add_to_layout(
                'v', extraformatsmarkdownQL, hlayout4, None)

        widget1 = QWidget()
        widget1.setLayout(tabwidget1_layout)
        widget2 = QWidget()
        widget2.setLayout(tabwidget2_layout)
        widget3 = QWidget()
        widget3.setLayout(tabwidget3_layout)
        widget4 = QWidget()
        widget4.setLayout(tabwidget4_layout)
        widget5 = QWidget()
        widget5.setLayout(tabwidget5_layout)
        tabWidget = QTabWidget()
        tabWidget.addTab(widget1, self.tr('General'))
        tabWidget.addTab(widget2, self.tr('Audio/Video'))
        tabWidget.addTab(widget3, self.tr('Images'))
        tabWidget.addTab(widget4, self.tr('Documents'))
        tabWidget.addTab(widget5, self.tr('Markdown'))

        buttonBox = QDialogButtonBox(
                QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        final_layout = utils.add_to_layout('v', tabWidget, None, buttonBox)
        self.setLayout(final_layout)

        self.defaultQTB.clicked.connect(self.open_dir)
        buttonBox.accepted.connect(self.save_settings)
        buttonBox.rejected.connect(self.reject)
        defvidcodecsQPB.clicked.connect(
                lambda: self.set_videocodecs(config.video_codecs))
        defaudcodecsQPB.clicked.connect(
                lambda: self.set_audiocodecs(config.audio_codecs))
        self.delete_cacheQPB.clicked.connect(
                lambda: self.delete_cache())

        self.resize(400, 450)
        self.setWindowTitle(self.tr('Preferences'))

        QTimer.singleShot(0, self.load_settings)

    def load_settings(self):
        """Load settings and update graphical widgets with loaded values."""
        settings = QSettings()
        mobile_ui = settings.value('mobile_ui', type=bool)
        disable_cache = settings.value('disable_cache', type=bool)
        overwrite_existing = settings.value('overwrite_existing', type=bool)
        default_output = settings.value('default_output', type=str)
        prefix = settings.value('prefix', type=str)
        suffix = settings.value('suffix', type=str)
        ffmpeg_path = settings.value('ffmpeg_path', type=str)
        default_command = (settings.value('default_command', type=str) or
                config.default_ffmpeg_cmd)
        videocodecs = (settings.value('videocodecs') or config.video_codecs)
        audiocodecs = (settings.value('audiocodecs') or config.audio_codecs)
        extraformats_video = (settings.value('extraformats_video') or [])
        default_command_image = (settings.value('default_command_image',
                type=str) or
                config.default_imagemagick_cmd
                )
        extraformats_image = (settings.value('extraformats_image') or [])
        extraformats_document = (settings.value('extraformats_document') or [])
        extraformats_markdown = (settings.value('extraformats_markdown') or [])
        extraformats_common = (settings.value('extraformats_common') or [])
        extraformats_double = (settings.value('extraformats_double') or [])

        if overwrite_existing:
            self.exst_overwriteQRB.setChecked(True)
        else:
            self.exst_prefixQRB.setChecked(True)
        self.disable_cacheQChB.setChecked(disable_cache)
        self.mobile_uiQChB.setChecked(mobile_ui)
        self.defaultQLE.setText(default_output)
        self.prefixQLE.setText(prefix)
        self.suffixQLE.setText(suffix)
        self.ffmpegpathQLE.setText(ffmpeg_path)
        self.ffmpegcmdQLE.setText(default_command)
        self.set_videocodecs(videocodecs)
        self.set_audiocodecs(audiocodecs)
        self.extraformatsffmpegQPTE.setPlainText("\n".join(extraformats_video))
        self.imagecmdQLE.setText(default_command_image)
        self.extraformatsimageQPTE.setPlainText("\n".join(extraformats_image))
        self.extraformatsdocumentQPTE.setPlainText("\n".join(extraformats_document))
        self.extraformatsmarkdownQPTE.setPlainText("\n".join(extraformats_markdown))
        self.commonformatsQPTE.setPlainText("\n".join(extraformats_common))
        self.doubleformatsQPTE.setPlainText("\n".join(extraformats_double))
        if os.name == 'nt':
            use_wsl = settings.value('use_wsl', type=bool)
            self.use_wslQChB.setChecked(use_wsl)

    def set_videocodecs(self, codecs):
        self.vidcodecsQPTE.setPlainText("\n".join(codecs))

    def set_audiocodecs(self, codecs):
        self.audcodecsQPTE.setPlainText("\n".join(codecs))

    def delete_cache(self):
        msg = QMessageBox(self)
        msg.setStandardButtons(QMessageBox.Ok)
        if os.path.exists(config.cache_file):
            os.remove(config.cache_file)
            msg.setIcon(QMessageBox.Information)
            msg.setText(self.tr("Cache file successfully deleted!"))
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText(self.tr("Cache file not found!"))
        msg.setWindowTitle(self.tr("Delete Cache"))
        msg.setModal(False)
        msg.show()

    def open_dir(self):
        """Get a directory name using a standard Qt dialog and update
        self.defaultQLE with dir's name."""
        if self.defaultQLE.isEnabled():
            _dir = QFileDialog.getExistingDirectory(
                    self, 'FF Multi Converter - ' +
                    self.tr('Choose default output destination'), config.home
                    )
            if _dir:
                self.defaultQLE.setText(_dir)

    @staticmethod
    def plaintext_to_list(widget, formats=[]):
        """
        Parse the text from a QPlainTextEdit widget and return a list.
        The list will consist of every text line that is a single word
        and it's not in the formats list. No duplicates allowed.
        """
        _list = []
        for line in widget.toPlainText().split("\n"):
            line = line.strip()
            if len(line.split()) == 1 and line not in (_list+formats):
                _list.append(line)
        return _list

    def save_settings(self):
        """Set settings values by extracting the appropriate information from
        the graphical widgets."""
        # set this to true if something that requires a restart was changed
        ui_change = False

        videocodecs = self.plaintext_to_list(self.vidcodecsQPTE)
        audiocodecs = self.plaintext_to_list(self.audcodecsQPTE)
        extraformats_video = self.plaintext_to_list(self.extraformatsffmpegQPTE,
                config.video_formats)
        extraformats_image = self.plaintext_to_list(self.extraformatsimageQPTE,
                config.image_formats)
        extraformats_document = self.plaintext_to_list(
                self.extraformatsdocumentQPTE, config.document_formats)
        extraformats_markdown = self.plaintext_to_list(
                self.extraformatsmarkdownQPTE, config.markdown_formats)
        extraformats_common = self.plaintext_to_list(
                self.commonformatsQPTE, config.common_formats)
        extraformats_double = self.plaintext_to_list(
                self.doubleformatsQPTE, config.double_formats)
        settings = QSettings()

        # WSL is irrelevant for everything but Windows, so should be false.
        if os.name == 'nt':
            use_wsl = self.use_wslQChB.isChecked()
        else:
            use_wsl = False

        ffmpeg_path = os.path.expanduser(self.ffmpegpathQLE.text())
        if not utils.is_installed(ffmpeg_path, use_wsl):
            ffmpeg_path = utils.is_installed('ffmpeg', use_wsl)

        # check if the UI was changed
        if settings.value('mobile_ui', type=bool) != self.mobile_uiQChB.isChecked():
            ui_change = True

        settings.setValue('mobile_ui', self.mobile_uiQChB.isChecked())
        settings.setValue('disable_cache', self.disable_cacheQChB.isChecked())
        settings.setValue('overwrite_existing', self.exst_overwriteQRB.isChecked())
        settings.setValue('default_output', self.defaultQLE.text())
        settings.setValue('prefix', self.prefixQLE.text())
        settings.setValue('suffix', self.suffixQLE.text())
        settings.setValue('ffmpeg_path', ffmpeg_path)
        settings.setValue('default_command', self.ffmpegcmdQLE.text())
        settings.setValue('videocodecs', sorted(videocodecs))
        settings.setValue('audiocodecs', sorted(audiocodecs))
        settings.setValue('extraformats_video', sorted(extraformats_video))
        settings.setValue('default_command_image', self.imagecmdQLE.text())
        settings.setValue('extraformats_image', sorted(extraformats_image))
        settings.setValue('extraformats_document', sorted(extraformats_document))
        settings.setValue('extraformats_markdown', sorted(extraformats_markdown))
        settings.setValue('extraformats_common', sorted(extraformats_common))
        settings.setValue('extraformats_double', sorted(extraformats_double))
        settings.setValue('use_wsl', use_wsl)

        if ui_change:
            ret = QMessageBox.question(self,'',
                self.tr("The changed settings require a program restart. Close Program?"),
                QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                self.accept()
                exit(0)
            else:
                # reset changes to mobile_ui and mobile_uiQChB
                settings.setValue('mobile_ui', not self.mobile_uiQChB.isChecked())
                self.mobile_uiQChB.setChecked(not self.mobile_uiQChB.isChecked())
        else:
            self.accept()
