# Copyright (C) 2023 l-koehler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QMessageBox

from ffmulticonverter import utils
from ffmulticonverter import config


class ValidationError(Exception):
    pass


class CompressionTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(CompressionTab, self).__init__(parent)
        self.name = 'Compression'
        self.formats = config.compression_formats
        
        convertQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        final_layout = utils.add_to_layout('h', convertQL, self.extQCB, None)
        self.setLayout(final_layout)

    def fill_extension_combobox(self, extraformats):
        self.extQCB.clear()
        self.extQCB.addItems(sorted(self.formats + extraformats))

    def ok_to_continue(self):
        """
        Check if everything is ok with compressiontab to continue conversion.

        Checks if:
        - tar            is missing.
        - ar             is missing.
        - squashfs-tools is missing.

        Return True if all tests pass, else False. TODO.
        """
        if not self.parent.pandoc:
            QMessageBox.warning(self, 'FF Multi Converter - ' +
                                self.tr('Error!'),
                                self.tr('Pandoc is not installed!'))
            return False
        return True
