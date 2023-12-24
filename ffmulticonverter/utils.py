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

"""
Various useful functions.
"""

import os
import re
import sys
import shlex
import subprocess
import time

from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import (
        QAction, QLayout, QLineEdit, QListWidget, QListWidgetItem, QMenu,
        QSpacerItem, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout
        )


def duration_in_seconds(duration):
    """
    Return the number of seconds of duration, an integer.
    Duration is a string of type hh:mm:ss.ts
    """
    duration = duration.split('.')[0] # get rid of milliseconds
    hours, mins, secs = [int(i) for i in duration.split(':')]
    return secs + (hours * 3600) + (mins * 60)

def is_installed(program):
    """
    If program is a program name, returns the absolute path to this program if
    included in the PATH enviromental variable, else empty string.

    If program is an absolute path, returns the path if it's executable, else
    empty sring.
    """
    program = os.path.expanduser(program)
    for path in os.getenv('PATH').split(os.pathsep):
        fpath = os.path.join(path, program)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return fpath
    return ''

def get_all_conversions():
    """
    the temporary list generated is a 3-dimensional mess.
    supported_tmp[converter_index][in/out] = [types]
    supported_tmp = [
    [[pandoc_in1, pandoc_in2], [pandoc_out1, pandoc_out2]],
    [[ffmpeg_in1, ffmpeg_in2], [ffmpeg_out1, ffmpeg_out2]],
    ]
    """
    supported_tmp = []
    # poll ffmpeg
    completed_process = subprocess.run(['ffmpeg', '-formats'],
                                   capture_output=True, text=True)
    ffmpeg_stdout = completed_process.stdout
    ffmpeg_input, ffmpeg_output = [], []
    ffmpeg_pattern = r'^\s*(DE|D|E)\s+(\S+)'    
    ffmpeg_stdout_lines = ffmpeg_stdout.splitlines()
    for line in ffmpeg_stdout_lines:
                match = re.match(ffmpeg_pattern, line)
                if match:
                    action, file_extension = match.groups()
                    if action == 'D' or action == 'DE':
                        ffmpeg_input.append(file_extension)
                    if action == 'E' or action == 'DE':
                        ffmpeg_output.append(file_extension)
    ffmpeg_conversions = [ffmpeg_input, ffmpeg_output]
    supported_tmp.append(ffmpeg_conversions)
    # poll pandoc
    completed_process = subprocess.run(['pandoc', '--list-input-formats'],
                                       capture_output=True, text=True)
    in_formats = completed_process.stdout
    in_format_list = in_formats.split('\n')
    if 'markdown' in in_format_list:
        in_format_list.append('md')
    completed_process = subprocess.run(['pandoc', '--list-output-formats'],
                                       capture_output=True, text=True)
    out_formats = completed_process.stdout
    out_format_list = out_formats.split('\n')
    if 'markdown' in out_format_list:
        out_format_list.append('md')
        
    pandoc_conversions = [in_format_list, out_format_list]
    supported_tmp.append(pandoc_conversions)
    # poll magick
    # TODO: clean this mess (but it works)
    completed_process = subprocess.run(['magick', 'identify', '-list', 'format'], capture_output=True, text=True)
    magick_formats = completed_process.stdout
    magick_format_list = magick_formats.split('\n')
    in_formats = []
    out_formats = []
    for line in magick_format_list:
        if '-'*len(line) == line:
            continue
        line_words = line.strip().split(' ')
        line_words = list(filter(None, line_words))
        if line_words == []:
            continue
        if not set(line_words[0]) <= set('ABCDEFTGHIJKLMNOPQRSTUVWXYZ*-'):
            continue
        file_format = line_words[0].replace("*","").lower()
        rw_status = line_words[2].replace("-","").replace("+","")
        if rw_status == "rw":
            in_formats.append(file_format)
            out_formats.append(file_format)
        elif rw_status == "r":
            in_formats.append(file_format)
        elif rw_status == "w":
            out_formats.append(file_format)
    magick_conversions = [in_formats, out_formats]
    supported_tmp.append(magick_conversions)
    # libreoffice exts
    # cant actually get those right now, so have some predefined lists instead
    calc  = [['csv', 'xls', 'xml', 'xlsx', 'ods', 'sdc'],
             ['csv', 'html', 'xls', 'xml', 'ods', 'sdc', 'xhtml']]
    img   = [['eps', 'emf', 'gif', 'jpg', 'odd', 'png', 'tiff', 'bmp', 'webp'],
             ['eps', 'emf', 'gif', 'html', 'jpg', 'odd', 'pdf', 'png', 'svg', 'tiff', 'bmp', 'xhtml', 'webp']]
    slide = [['odp', 'ppt', 'pptx', 'sda'],
             ['eps', 'gif', 'html', 'swf', 'odp', 'ppt', 'pdf', 'svg', 'sda', 'xml']]
    text  = [['xml', 'html', 'doc', 'docx', 'odt', 'txt', 'rtf', 'sdw'],
             ['bib', 'xml', 'html', 'ltx', 'doc', 'odt', 'txt', 'pdf', 'rtf', 'sdw']]
    supported_tmp.append(calc)
    supported_tmp.append(img)
    supported_tmp.append(slide)
    supported_tmp.append(text)
    return supported_tmp

def get_ext_conversions(extension):
    possible_conversions = []
    # TODO: get_all_conversions is SLOW, run at start once
    all_conversions = get_all_conversions()
    for converter in all_conversions:
        if extension in converter[0]:
            possible_conversions.append(converter[0])
    return possible_conversions

def start_office_listener():
    """
    Start a openoffice/libreoffice listener.
    We need an open office listener in order to make convertions with unoconv.
    """
    # note: we cannot kill the listener with p.kill() as it is a spawned process
    # the office listener remains open even after program's termination
    # the listener starts at port 2003 (default:2002) to allow for easier kill
    p = subprocess.Popen(shlex.split("unoconv --listener --port 2003"))
    while p.poll() is not None:
        time.sleep(0.1)
    time.sleep(1) # wait for listener to setup correctly

def find_presets_file(fname, lookup_dirs, lookup_virtenv):
    """
    The default presets.xml could be stored in different locations during
    the installation depending on different Linux distributions.
    Search for this file on each possible directory to which user
    specific data files could be stored.

    Keyword arguments:
    fname          -- file name
    lookup_dirs    -- list of the directories to search for fname
    lookup_virtent -- directory to search for fname in virtualenv

    Return the path of the file if found, else an empty string.
    """
    possible_dirs = os.environ.get(
            "XDG_DATA_DIRS", ":".join(lookup_dirs)
            ).split(":")
    # for virtualenv installations
    posdir = os.path.realpath(
            os.path.join(os.path.dirname(sys.argv[0]), '..', lookup_virtenv))
    if not posdir in possible_dirs:
        possible_dirs.append(posdir)

    for _dir in possible_dirs:
        _file = os.path.join(_dir, 'ffmulticonverter/' + fname)
        if os.path.exists(_file):
            return _file

    # when program is not installed or running from test_dialogs.py
    return os.path.dirname(os.path.realpath(__file__)) + '/../share/' + fname

def create_paths_list(
        files_list, ext_to, prefix, suffix, output, orig_dir,
        overwrite_existing
        ):
    """
    Create and return a list with dicts.
    Each dict will have only one key and one corresponding value.
    Key will be a file to be converted and it's value will be the name
    of the new converted file.

    Example list:
    [{"/foo/bar.png" : "/foo/bar.bmp"}, {"/f/bar2.png" : "/f/bar2.bmp"}]

    Keyword arguments:
    files_list -- list with files to be converted
    ext_to     -- the extension to which each file must be converted to
    prefix     -- string that will be added as a prefix to all filenames
    suffix     -- string that will be added as a suffix to all filenames
    output     -- the output folder
    orig_dir   -- if True, each file will be saved at its original directory
                  else, files will be saved at output
    overwrite_existing -- if False, a '~' will be added as prefix to
                          filenames
    """
    assert ext_to.startswith('.'), 'ext_to must start with a dot (.)'

    conversion_list = []
    dummy = []

    for _file in files_list:
        _dir, name = os.path.split(_file)
        y = prefix + os.path.splitext(name)[0] + suffix + ext_to

        if orig_dir:
            y = _dir + '/' + y
        else:
            y = output + '/' + y

        if not overwrite_existing:
            while os.path.exists(y) or y in dummy:
                _dir2, _name2 = os.path.split(y)
                y = _dir2 + '/~' + _name2

        dummy.append(y)
        # Add quotations to paths in order to avoid error in special
        # cases such as spaces or special characters.
        _file = '"' + _file + '"'
        y = '"' + y + '"'

        _dict = {}
        _dict[_file] = y
        conversion_list.append(_dict)

    return conversion_list

def update_cmdline_text(command, _filter, regex, add, gindex1, gindex2):
    """
    Update and return the command line text by adding, removing or edditing a
    ffmpeg filter based on the given regular expression.

    Keyword arguments:
    command  -- initial command text (string)
    _filter  -- ffmpeg filter to add or edit in command (string)
    regex    -- regex to search in command
    add      -- if True, add filter to command, else filter must be removed
    gindex1  -- group index of the first group before filter group in regex
    gindex2  -- group index of the first group after filter group in regex
    """
    regex2 = r'(-vf "[^"]*)"'
    regex3 = r'-vf +([^ ]+)'

    search = re.search(regex, command)
    if search:
        if add:
            command = re.sub(
                    regex,
                    r'\{0}{1}\{2}'.format(gindex1+1, _filter, gindex2+1),
                    command
                    )
        else:
            group1 = search.groups()[gindex1].strip()
            group2 = search.groups()[gindex2].strip()
            if group1 and group2:
                # the filter is between 2 other filters
                # remove it and leave a comma
                command = re.sub(regex, ',', command)
            else:
                # remove filter
                command = re.sub(regex, _filter, command)
                # add a space between -vf and filter if needed
                command = re.sub(r'-vf([^ ])', r'-vf \1', command)
                if not group1 and not group2:
                    # remove -vf option
                    command = re.sub(r'-vf *("\s*"){0,1}', '', command)
    elif re.search(regex2, command):
        command = re.sub(regex2, r'\1,{0}"'.format(_filter), command)
    elif re.search(regex3, command):
        command = re.sub(regex3, r'-vf "\1,{0}"'.format(_filter), command)
    elif _filter:
        command += ' -vf "' + _filter + '"'

    return re.sub(' +', ' ', command).strip()


#######################################################################
# Useful pyqt-related functions to automate some parts of ui creation.
#######################################################################

def add_to_layout(layout, *items):
    """Add items to QVBox and QHBox layouts easily.

    Keyword arguments:
    layout -- a layout oject (QVBoxLayout or QHBoxLayout) or a string
              if "v" or "h" create a QVBox or QHBox respectively
    *items -- list with items to be added
    """
    if isinstance(layout, str):
        if layout == "v":
            layout = QVBoxLayout()
        elif layout == "h":
            layout = QHBoxLayout()
        else:
            raise TypeError("Invalid layout!")

    for item in items:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif isinstance(item, QLayout):
            layout.addLayout(item)
        elif isinstance(item, QSpacerItem):
            layout.addItem(item)
        elif item is None:
            layout.addStretch()
        else:
            raise TypeError("Argument of wrong type!")
    return layout

def add_to_grid(*items):
    """Add items to a QGrid layout easily.

    Keyword arguments:
    *items -- list with lists of items to be added.
              items in the same list will be added to the same line of grid.
    """
    layout = QGridLayout()
    # for now it adds only 1 item per cell.
    for x, _list in enumerate(items):
        for y, item in enumerate(_list):
            if isinstance(item, QWidget):
                layout.addWidget(item, x, y)
            elif isinstance(item, QLayout):
                layout.addLayout(item, x, y)
            elif isinstance(item, QSpacerItem):
                layout.addItem(item, x, y)
            elif item is None:
                pass
            else:
                raise TypeError("Argument of wrong type!")
    return layout

def create_action(parent, text, shortcut=None, icon=None, tip=None,
                  triggered=None, toggled=None, context=Qt.WindowShortcut):
    """Create a QAction with the given attributes."""
    action = QAction(text, parent)
    if triggered is not None:
        action.triggered.connect(triggered)
    if toggled is not None:
        action.toggled.connect(toggled)
        action.setCheckable(True)
    if icon is not None:
        action.setIcon( icon )
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    action.setShortcutContext(context)
    return action

def add_actions(target, actions, insert_before=None):
    """Add actions to menu.

    Keyword arguments:
    target -- menu to add action
    actions -- list with actions to add
    """
    previous_action = None
    target_actions = list(target.actions())
    if target_actions:
        previous_action = target_actions[-1]
        if previous_action.isSeparator():
            previous_action = None
    for action in actions:
        if (action is None) and (previous_action is not None):
            if insert_before is None:
                target.addSeparator()
            else:
                target.insertSeparator(insert_before)
        elif isinstance(action, QMenu):
            if insert_before is None:
                target.addMenu(action)
            else:
                target.insertMenu(insert_before, action)
        elif isinstance(action, QAction):
            if insert_before is None:
                target.addAction(action)
            else:
                target.insertAction(insert_before, action)
        previous_action = action

def create_LineEdit(maxsize, validator, maxlength):
    """Create a lineEdit with the given attributes.

    Keyword arguments:
    maxsize -- maximum size
    validator -- a QValidator
    maxlength - maximum length

    Returns: QLineEdit
    """
    lineEdit = QLineEdit()
    if maxsize is not None:
        lineEdit.setMaximumSize(QSize(maxsize[0], maxsize[1]))
    if validator is not None:
        lineEdit.setValidator(validator)
    if maxlength is not None:
        lineEdit.setMaxLength(maxlength)
    return lineEdit


######################
# Custom pyqt widgets
######################

class XmlListItem(QListWidgetItem):
    def __init__(self, text, xml_element, parent=None):
        super(XmlListItem, self).__init__(text, parent)
        self.xml_element = xml_element


class FilesList(QListWidget):
    dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super(FilesList, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(url.toLocalFile())
            self.dropped.emit(links)
        else:
            event.ignore()
