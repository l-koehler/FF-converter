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

"""
Various useful functions.
"""

import os
import re
import sys
import shlex
import subprocess
import time
import string
import threading
import importlib.util

from PyQt5.QtCore import pyqtSignal, QSize, Qt, QSettings
from PyQt5.QtWidgets import (
        QAction, QLayout, QLineEdit, QListWidget, QListWidgetItem, QMenu,
        QSpacerItem, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout
        )
from ffconverter import config

class ThreadWithReturn(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)

def duration_in_seconds(duration):
    """
    Return the number of seconds of duration, an integer.
    Duration is a string of type hh:mm:ss.ts
    """
    duration = duration.split('.')[0] # get rid of milliseconds
    hours, mins, secs = [int(i) for i in duration.split(':')]
    return secs + (hours * 3600) + (mins * 60)

def is_installed(program, use_wsl, wsl_only=False):
    """
    If program is a program name, returns the absolute path to this program if
    included in the PATH enviromental variable, else empty string.

    If program is an absolute path, returns the path if it's executable, else
    empty string.
    """

    if program.startswith('wsl'): return program # do not resolve WSL paths

    # python packages
    if program == 'trimesh':
        is_installed = False
        if importlib.util.find_spec(program) is not None:
            is_installed = importlib.util.find_spec(program).loader is not None
        return is_installed

    # wsl_only is used to not get "convert" on a windows system
    if wsl_only == False:
        path_env = os.getenv('PATH').split(os.pathsep)
        for path in path_env:
            fpath = os.path.join(path, program)
            if os.name == 'nt':
                fpath_ls = [fpath, fpath+'.exe', fpath+'.cmd', fpath+'.bat']
            else:
                fpath_ls = [fpath, fpath+'.sh']
            for fpath in fpath_ls:
                if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
                    return fpath
        # imagemagick 6 uses 'convert', version 7 uses 'magick'
        # 'convert' is reserved for fat-to-ntfs conversion in windows
        if program == 'magick' and os.name != 'nt':
            return is_installed('convert', False)

    # only if nothing was found on the regular system, check WSL
    if use_wsl == True:
        # Add 'wsl -- echo $PATH'
        try:
            wsl_which = subprocess.check_output(["wsl", "--", "which", program], stderr = subprocess.STDOUT)
            wsl_which = wsl_which.decode('utf-8')
            if not wsl_which.startswith('which: no '):
                fpath = 'wsl -- ' + wsl_which.split('\n')[0]
                return fpath
        except subprocess.CalledProcessError:
            pass

    return ''

def wsl_adjust(use_wsl, command, path1="", path2=""):
    # This function will always be called, but isn't needed if WSL can't be used
    # this also is the only case where it won't forcibly adjust all paths to use
    # slashes as pathsep.
    if not use_wsl:
        return [command, path1, path2]

    # unquote command and
    # get the full path of the command (might also be a wsl command)
    command = command.replace("\"", "")
    full_command = is_installed(command, use_wsl)

    def adjust_path(path, force_unix_paths):
        # unquote path
        # also always replace backslashes, windows can handle regular ones
        path = path.replace('\"', '').replace('\\', '/')
        # replace D:/whatever with /mnt/d/whatever for WSL commands
        if force_unix_paths:
            drive_letter = path[0]
            wsl_path = path[2:] # remove drive letter
            wsl_path = '\"/mnt/' + drive_letter.lower() + wsl_path + '\"'
            return wsl_path
        return path

    # properly quote command, just in case there are spaces or stuff in the path
    force_unix_paths = False
    if full_command.startswith('wsl -- '):
        force_unix_paths = True
        full_command = 'wsl -- \"' + full_command[7:] + '\"'
    else:
        full_command = '\"' + full_command + '\"'

    return_list = [full_command.replace('\\', '/'),
        adjust_path(path1, force_unix_paths),
        adjust_path(path2, force_unix_paths)]
    return return_list

def get_all_conversions(settings, get_conv_for_ext = False,
                        ext = ["",""], missing = [], use_wsl = False):
    """
    generates a nested list. how to access:
    supported_tmp[converter_index][in/out] = [types]
    the list looks something like this
    supported_tmp = [
    [[pandoc_in1, pandoc_in2], [pandoc_out1, pandoc_out2]],
    [[ffmpeg_in1, ffmpeg_in2], [ffmpeg_out1, ffmpeg_out2]],
    ]
    """
    """
    Defaults to returning all supported conversions, but can also return
    the converter for a conversion given as:
    ext =  [input_ext, output_ext]
    if get_conv_for_ext is True.
    """
    supported_tmp = []

    # poll ffmpeg
    if 'ffmpeg' not in missing:
        extraformats_video = (settings.value('extraformats_video') or [])
        completed_process = subprocess.run(['ffmpeg', '-formats'],
                                    capture_output=True, text=True)
        ffmpeg_stdout = completed_process.stdout
        ffmpeg_input, ffmpeg_output = [], []
        ffmpeg_stdout_lines = ffmpeg_stdout.splitlines()
        for line in ffmpeg_stdout_lines:
            line_args = line.split()
            action = line_args[0]
            # dont run on the header lines
            pattern = r'^\s*(DE|D|E)\s+(\S+)'
            match = re.match(pattern, line)
            if not match:
                continue

            # line_args[1] can be "ext" or "ext1,ext2", so a split is neccesary
            extension = line_args[1].split(',')
            if 'D' in action:
                ffmpeg_input += extension
            if 'E' in action:
                ffmpeg_output += extension
        ffmpeg_conversions = [ffmpeg_input + extraformats_video,
                              ffmpeg_output + extraformats_video]
        supported_tmp.append(ffmpeg_conversions)
    else:
        ffmpeg_conversions = [[], []]

    # poll pandoc
    if 'pandoc' not in missing:
        extraformats_markdown = (settings.value('extraformats_markdown') or [])
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
        pandoc_conversions = [in_format_list + extraformats_markdown,
                              out_format_list + extraformats_markdown]
        supported_tmp.append(pandoc_conversions)
    else:
        pandoc_conversions = [[], []]

    # poll magick
    if 'imagemagick' not in missing:
        extraformats_image = (settings.value('extraformats_image') or [])
        try:
            completed_process = subprocess.run(['magick', 'identify', '-list',
                                                'format'],
                                            capture_output=True, text=True)
        except FileNotFoundError:
            # retry with convert
            if use_wsl:
                cmd = ['wsl', '--', 'convert', 'identify', '-list', 'format']
            else:
                cmd = ['convert', 'identify', '-list', 'format']
            completed_process = subprocess.run(cmd, capture_output=True, text=True)
        magick_formats = completed_process.stdout
        magick_format_list = magick_formats.split('\n')
        in_formats = []
        out_formats = []
        for line in magick_format_list:
            line_args = line.split()
            # if the line is empty or does not start with all-caps (EXTENSION)
            uppercase_chars = string.ascii_uppercase + '*-'
            if len(line_args) < 3 or set(line_args[0]) <= set(uppercase_chars):
                continue
            file_format, module, rw_status = line_args[:3]
            file_format = file_format.lower().replace('*', '')
            if module in ['BRAILLE', 'TXT']:
                continue
            if "r" in rw_status:
                # the program will break trying to read some PDFs
                if module not in ['PDF']:
                    in_formats.append(file_format)
            if "w" in rw_status:
                out_formats.append(file_format)
        # for formats like PNG, the output will be PNG00 .. PNG64.
        if 'png00' in in_formats and 'png' not in in_formats:
            in_formats.append('png')
        if 'png00' in out_formats and 'png' not in out_formats:
            out_formats.append('png')
        magick_conversions = [in_formats + extraformats_image,
                              out_formats + extraformats_image]
        supported_tmp.append(magick_conversions)
    else:
        magick_conversions = [[], []]

    # libreoffice exts
    # cant actually get those right now, so have some predefined lists instead
    if 'unoconv' not in missing:
        extraformats_document = (settings.value('extraformats_document') or [])
        calc  = [['csv', 'xls', 'xml', 'xlsx', 'ods', 'sdc'] + extraformats_document,
                ['csv', 'html', 'xls', 'xml', 'ods', 'sdc', 'xhtml'] + extraformats_document]
        img   = [['eps', 'emf', 'gif', 'jpg', 'odd', 'png', 'tiff', 'bmp', 'webp'] + extraformats_document,
                ['eps', 'emf', 'gif', 'html', 'jpg', 'odd', 'pdf', 'png', 'svg', 'tiff', 'bmp', 'xhtml', 'webp'] + extraformats_document]
        slide = [['odp', 'ppt', 'pptx', 'sda'] + extraformats_document,
                ['eps', 'gif', 'html', 'swf', 'odp', 'ppt', 'pdf', 'svg', 'sda', 'xml'] + extraformats_document]
        text  = [['xml', 'html', 'doc', 'docx', 'odt', 'txt', 'rtf', 'sdw', 'pdf'] + extraformats_document,
                ['bib', 'xml', 'html', 'ltx', 'doc', 'odt', 'txt', 'pdf', 'rtf', 'sdw'] + extraformats_document]
        supported_tmp.append(calc)
        supported_tmp.append(img)
        supported_tmp.append(slide)
        supported_tmp.append(text)
    else:
        calc = [[], []]
        img = [[], []]
        slide = [[], []]
        text = [[], []]

    # compression exts
    # same as above
    extraformats_compression = (settings.value('extraformats_compression')
                                or [])
    compression_exts = [[], []]
    if 'tar' not in missing:
        compression_exts[0] += ['tar']
        compression_exts[1] += ['tar']
        if 'gzip' not in missing:
            compression_exts[0] += ['tgz', 'tar.gz']
            compression_exts[1] += ['tgz', 'tar.gz']
        if 'bzip2' not in missing:
            compression_exts[0] += ['tar.bz2']
            compression_exts[1] += ['tar.bz2']
    # zip and unzip are separate for some reason
    if 'unzip' not in missing:
        compression_exts[0] += ['zip']
    if 'zip' not in missing:
        compression_exts[1] += ['zip']
    if 'squashfs-tools' not in missing:
        compression_exts[0] += ['sqfs', 'squashfs', 'snap']
        compression_exts[1] += ['squashfs']
    if 'ar/binutils' not in missing:
        compression_exts[0] += ['deb', 'a', 'ar', 'o', 'so']
        compression_exts[1] += ['ar']
    if compression_exts != [[], []]: # if any of the tools work
        compression_exts[0] += extraformats_compression
        compression_exts[1] += extraformats_compression + ['[Folder]']
    supported_tmp.append(compression_exts)

    model_exts = [[], []]
    if 'trimesh' not in missing:
        # TODO: trimesh can load/export far more types, add these
        model_exts[0] += ['step']
        model_exts[1] += ['stl']
    supported_tmp.append(model_exts)

    # if the function is meant to return a converter for a in/output pair
    if get_conv_for_ext:
        if ext[0] in ffmpeg_conversions[0] and ext[1] in ffmpeg_conversions[1]:
            return "ffmpeg"
        elif ext[0] in pandoc_conversions[0] and ext[1] in pandoc_conversions[1]:
            return "pandoc"
        elif ext[0] in magick_conversions[0] and ext[1] in magick_conversions[1]:
            return "magick"
        elif ext[0] in calc[0] and ext[1] in calc[1]:
            return "soffice"
        elif ext[0] in img[0] and ext[1] in img[1]:
            return "soffice"
        elif ext[0] in slide[0] and ext[1] in slide[1]:
            return "soffice"
        elif ext[0] in text[0] and ext[1] in text[1]:
            return "soffice"
        elif ext[0] in compression_exts[0] and ext[1] in compression_exts[1]:
            return "compression"
        elif ext[0] in model_exts[0] and ext[1] in model_exts[1]:
            return "trimesh"
        else:
            return "unsupported"
    else:
        return supported_tmp

def get_extension(file_path):
    """
    Given a file path (or name, the file isn't opened),
    return a extension without leading dot.
    It the extension is in config.double_formats, the double format
    will be returned (e.g. 'tar.gz').
    """

    # if there are quotation marks around the file path, remove them
    settings = QSettings()

    file_path = file_path.replace("\"", "")

    remainder, first_ext = os.path.splitext(file_path)
    first_ext = first_ext[1:]
    second_ext = os.path.splitext(remainder)[-1][1:] # '' if only one ext there
    joined_ext = second_ext + '.' + first_ext

    all_double = config.double_formats + (settings.value('extraformats_double') or [])
    if joined_ext in all_double:
        return joined_ext.lower()
    return first_ext.lower()

def get_combobox_content(self, list_of_files, all_supported_conversions,
                         common=[]):
    possible_outputs = []
    for input_file in list_of_files:
        file_outputs = []
        input_file_ext = get_extension(input_file)
        for conv in all_supported_conversions:
            if input_file_ext in conv[0]:
                # append to possible_outputs only once per file
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
        # flatten and deduplicate
        first_output_list = possible_outputs[0] if possible_outputs else []
        valid_outputs = list(dict.fromkeys(first_output_list))

    if [ext for ext in valid_outputs if ext in common] != []:
        # remove all uncommon formats from the list
        valid_outputs[:] = [ext for ext in valid_outputs if ext in common]
    return valid_outputs

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
        _file = os.path.join(_dir, 'ffconverter/' + fname)
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
        # name[:-len('.'+ext_from)] is the name without extension
        ext_from = get_extension(name)
        y = prefix + name[:-len('.'+ext_from)] + suffix + ext_to

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
