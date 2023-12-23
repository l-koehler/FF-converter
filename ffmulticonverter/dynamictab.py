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


class DynamicTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(DynamicTab, self).__init__(parent)
        self.name = 'Dynamic'
        self.formats = [] # Change on File set
        
        convertQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        final_layout = utils.add_to_layout('h', convertQL, self.extQCB, None)
        self.setLayout(final_layout)

    """
    This function is different from the other fill_extension_combobox functions,
    as it takes a list of all files in the file list and fills
    conversions into any supported type into the combobox.
    """
    def fill_extension_combobox(self, list_of_files):
        self.extQCB.clear()
        supported_formats = []
        for input_file in list_of_files:
            # TODO: actually figure out what extensions are supported
            supported_formats.append(input_file)
        self.extQCB.addItems(sorted(supported_formats))

    def ok_to_continue(self):
        return True
