# Copyright (C) 2023-2024 l-koehler
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

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QMessageBox, QCheckBox

import os
from ffconverter import utils
from ffconverter import config


class ValidationError(Exception):
    pass


class DynamicTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(DynamicTab, self).__init__(parent)
        self.name = 'Dynamic'
        self.formats = [] # Change on File set

        self.commonformatQChB = QCheckBox(self.tr("Only show common formats"))
        convertQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()

        hlayout1 = utils.add_to_layout('h', convertQL, self.extQCB, None)
        hlayout2 = utils.add_to_layout('h', self.commonformatQChB)
        final_layout = utils.add_to_layout('v', hlayout1, hlayout2)
        self.setLayout(final_layout)
        
        
        # default to only common formats
        self.commonformatQChB.setChecked(True)
        self.commonformatQChB.stateChanged.connect(parent.filesList_update)

    """
    This function is different from the other fill_extension_combobox functions,
    as it takes a list of all files in the file list and fills
    conversions into any supported type into the combobox.
    """
    def fill_extension_combobox(self, list_of_files, all_supported_conversions):
        self.extQCB.clear()
        possible_outputs = []
        for input_file in list_of_files:
            file_outputs = []
            input_file_ext = utils.get_extension(input_file)
            for conv in all_supported_conversions:
                if input_file_ext in conv[0]:
                    # append only once per file
                    file_outputs += conv[1]
            possible_outputs.append(file_outputs)
        # possible_outputs: list of lists of output formats, one per input file
        # valid_outputs: list of outputs possible for ALL files
        if len(list_of_files) > 1:
            valid_outputs = []
            for extension in sum(possible_outputs, []):
                available = True
                for i in possible_outputs:
                    if extension not in i:
                        available = False
                        break
                if available and extension not in valid_outputs:
                    valid_outputs.append(extension)
        else:
            first_output_list = possible_outputs[0] if possible_outputs else []
            valid_outputs = list(dict.fromkeys(first_output_list))

        if self.commonformatQChB.isChecked():
            # remove all uncommon formats from the list
            valid_outputs[:] = [ext for ext in valid_outputs
                                if ext in config.common_formats]
        self.extQCB.addItems(sorted(valid_outputs))

    def ok_to_continue(self):
        return True
