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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import io
import signal
import threading
import subprocess
import shlex
import shutil
import logging
import sys
import uuid
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
        QApplication, QDialog, QFrame, QLabel, QPushButton, QProgressBar,
        QMessageBox, QTextEdit, QCommandLinkButton, QSizePolicy, QCheckBox
        )

from ffconverter import utils
from ffconverter import config


def kill_process_tree(child):
    """
    Kill a child process together with the processes it spawned.

    LibreOffice forks helper processes, so killing only the direct child can
    leave orphans behind. The child is started in its own session (see
    convert_document), so on POSIX it can be killed as a process group.
    """
    if os.name != 'nt':
        try:
            os.killpg(os.getpgid(child.pid), signal.SIGKILL)
            return
        except (ProcessLookupError, PermissionError, OSError):
            pass
    child.kill()


class Progress(QDialog):
    file_converted_signal = pyqtSignal()
    update_text_edit_signal = pyqtSignal(str)

    def __init__(self, files, tab, delete, parent, test=False):
        """
        Keyword arguments:
        files  -- list with dicts containing file names
        tab -- instance of AudioVideoTab, ImageTab etc,
               indicating currently active tab
        delete -- boolean that shows if files must removed after conversion
        parent -- parent widget

        files:
        Each dict has only one key with one corresponding value.
        The key is the file to be converted and its value is
        the path of the file that will be created by conversion.

        Example list:
        [{"/foo/bar.png" : "/foo/bar.bmp"}, {"/f/bar2.png" : "/f/bar2.bmp"}]
        """
        super(Progress, self).__init__(parent)
        self.parent = parent

        self.files = files
        self.num_total_files = len(self.files)
        self.tab = tab
        self.delete = delete
        if not test:
            self._type = tab.name
        self.ok = 0
        self.error = 0
        self.running = True
        self._procs = []

        self.nowQL = QLabel(self.tr('In progress: '))
        self.nowQPBar = QProgressBar()
        self.nowQPBar.setValue(0)
        self.shutdownQCB = QCheckBox(
            self.tr('System shutdown after conversion'))
        self.cancelQPB = QPushButton(self.tr('Cancel'))

        detailsQPB = QCommandLinkButton(self.tr('Details'))
        detailsQPB.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        detailsQPB.setCheckable(True)
        detailsQPB.setMaximumWidth(113)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.outputQTE = QTextEdit()
        self.outputQTE.setReadOnly(True)
        self.frame = QFrame()
        frame_layout = utils.add_to_layout('h', self.outputQTE)
        self.frame.setLayout(frame_layout)
        self.frame.hide()

        hlayout1 = utils.add_to_layout('h', None, self.nowQL, None)
        hlayout2 = utils.add_to_layout('h', detailsQPB, line)
        hlayout3 = utils.add_to_layout('h', self.frame)
        hlayout4 = utils.add_to_layout('h', None, self.cancelQPB)
        vlayout = utils.add_to_layout(
                'v', hlayout1, self.nowQPBar, hlayout2, hlayout3,
                self.shutdownQCB, hlayout4
                )
        self.setLayout(vlayout)

        detailsQPB.toggled.connect(self.resize_dialog)
        detailsQPB.toggled.connect(self.frame.setVisible)
        self.cancelQPB.clicked.connect(self.reject)
        self.file_converted_signal.connect(self.next_file)
        self.update_text_edit_signal.connect(self.update_text_edit)

        self.resize(484, 190)
        self.setWindowTitle('FF Multi Converter - ' + self.tr('Conversion'))

        if not test:
            self.get_data() # should be first and not in QTimer.singleShot()
            QTimer.singleShot(0, self.manage_conversions)

    def get_data(self):
        """Collect conversion data from parents' widgets."""
        if self._type == 'AudioVideo':
            self.cmd = self.tab.commandQLE.text()
        elif self._type == 'Images':
            width = self.tab.widthQLE.text()
            self.size = ''
            self.mntaspect = False
            if width:
                height = self.tab.heightQLE.text()
                self.size = '{0}x{1}'.format(width, height)
                self.mntaspect = self.tab.imgaspectQChB.isChecked()
            self.imgcmd = self.tab.commandQLE.text()
            if self.tab.autocropQChB.isChecked():
                self.imgcmd += ' -trim +repage'
            rotate = self.tab.rotateQLE.text().strip()
            if rotate:
                self.imgcmd += ' -rotate {0}'.format(rotate)
            if self.tab.vflipQChB.isChecked():
                self.imgcmd += ' -flip'
            if self.tab.hflipQChB.isChecked():
                self.imgcmd += ' -flop'

    def resize_dialog(self):
        """Resize dialog"""
        height = 190 if self.frame.isVisible() else 450
        self.setMinimumSize(484, height)
        self.resize(484, height)

    def update_text_edit(self, txt):
        """Append txt to the end of current self.outputQTE's text."""
        current = self.outputQTE.toPlainText()
        self.outputQTE.setText(current+txt)
        self.outputQTE.moveCursor(QTextCursor.End)

    def manage_conversions(self):
        """
        Check whether all files have been converted.
        If not, it will allow convert_a_file() to convert the next file.
        """
        if not self.running:
            return
        if not self.files:
            sum_files = self.ok + self.error
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            if self.error:
                # not all files have been converted
                msg.setIcon(QMessageBox.Critical)
            else:
                # all files have been converted
                msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(self.tr("Report"))
            msg.setText(self.tr("Converted: {0}/{1}".format(self.ok,sum_files)))
            msg.setModal(False)
            msg.show()

            self.cancelQPB.setText(self.tr("Close"))

            if self.shutdownQCB.isChecked():
                # Locating systemctl in WSL would be pointless, use_wsl is False
                if utils.is_installed('systemctl', False):
                    subprocess.call(shlex.split('systemctl poweroff'))
                else:
                    subprocess.call(shlex.split('shutdown -h now'))
        else:
            self.convert_a_file()

    def next_file(self):
        """
        Update progress bar value, remove converted file from self.files
        and call manage_conversions() to continue the process.
        """
        self.nowQPBar.setValue(100)
        QApplication.processEvents()
        self.files.pop(0)
        self.manage_conversions()

    def reject(self):
        """
        Use standard dialog to ask whether procedure must stop or not.
        Use the SIGSTOP to stop the conversion process while waiting for user
        to respond and SIGCONT or kill depending on user's answer.
        """
        if not self.files:
            QDialog.accept(self)
            return
        if self._type == 'AudioVideo':
            self.process.send_signal(signal.SIGSTOP)
        self.running = False
        reply = QMessageBox.question(
                self,
                'FF Multi Converter - ' + self.tr('Cancel Conversion'),
                self.tr('Are you sure you want to cancel conversion?'),
                QMessageBox.Yes|QMessageBox.Cancel
                )
        if reply == QMessageBox.Yes:
            if self._type == 'AudioVideo':
                self.process.kill()
            for proc in self._procs:
                try:
                    proc.terminate()
                except OSError:
                    pass
            self.running = False
            if hasattr(self, 'thread'):
                self.thread.join()
            QDialog.reject(self)
        if reply == QMessageBox.Cancel:
            self.running = True
            if self._type == 'AudioVideo':
                self.process.send_signal(signal.SIGCONT)
            else:
                self.manage_conversions()

    def convert_a_file(self):
        """
        Update self.nowQL's text with current file's name, set self.nowQPBar
        value to zero and start the conversion procedure in a second thread
        using threading module.
        """
        if not self.files:
            return
        from_file = list(self.files[0].keys())[0]
        to_file = list(self.files[0].values())[0]

        text = os.path.basename(from_file[1:-1])
        num_file = self.num_total_files - len(self.files) + 1
        text += ' ({0}/{1})'.format(num_file, self.num_total_files)

        self.nowQL.setText(self.tr('In progress:') + ' ' + text)
        self.nowQPBar.setValue(0)

        if not os.path.exists(from_file[1:-1]):
            self.error += 1
            self.file_converted_signal.emit()
            return

        def convert():
            if self._type == 'AudioVideo':
                conv_func = self.convert_video
                params = (from_file, to_file, self.cmd)
            elif self._type == 'Images':
                conv_func = self.convert_image
                params = (from_file, to_file, self.size, self.mntaspect,
                          self.imgcmd)
            elif self._type == 'Markdown':
                conv_func = self.convert_markdown
                params = (from_file, to_file)
            elif self._type == "Compression":
                conv_func = self.convert_compression
                params = (from_file, to_file, self.parent.all_supported_conversions)
            elif self._type == "Documents":
                conv_func = self.convert_document
                params = (from_file, to_file, self.parent.all_supported_conversions)
            else:
                conv_func = self.convert_dynamic
                params = (from_file, to_file, converter, self.parent.all_supported_conversions)

            try:
                if conv_func(*params):
                    self.ok += 1
                    if self.delete and not from_file == to_file:
                        try:
                            os.remove(from_file[1:-1])
                        except OSError:
                            pass
                else:
                    self.error += 1
            except Exception as e:
                # convert() caused a exception, likely a wrong command was used.
                self.update_text_edit_signal.emit(f"Exception in convert(): {e}\n")
                self.error += 1

            self.file_converted_signal.emit()

        force_no_thread = False
        # trimesh doesn't work with threads
        if self._type not in ['AudioVideo', 'Images', 'Markdown', 'Compression', 'Documents']:
            from_file_ext = utils.get_extension(from_file, self.parent.all_supported_conversions)
            to_file_ext = utils.get_extension(to_file, self.parent.all_supported_conversions)
            converter = utils.get_all_conversions(self.parent.settings, 
                                                get_conv_for_ext=True,
                                                ext=[from_file_ext,to_file_ext],
                                                missing=self.parent.missing,
                                                use_wsl=self.parent.use_wsl)
            if converter == "trimesh":
                convert()
            else:
                self.thread = threading.Thread(target=convert)
                self.thread.start()
        else:
            self.thread = threading.Thread(target=convert)
            self.thread.start()

    def convert_video(self, from_file, to_file, command):
        """
        Create the ffmpeg command and execute it in a new process using the
        subprocess module. While the process is alive, parse ffmpeg output,
        estimate conversion progress using video's duration.
        With the result, emit the corresponding signal in order progress bar
        to be updated. Also emit regularly the corresponding signal in order
        an outputQTE to be updated with ffmpeg's output. Finally, save log
        information.

        Return True if conversion succeed, else False.
        """
        # note: from_file and to_file names are inside quotation marks
        convert_cmd = '{0} -y -i {1} {2} {3}'.format(
                self.parent.ffmpeg_path.replace("\\", "/"),
                from_file, command, to_file)
        self.update_text_edit_signal.emit(convert_cmd + '\n')

        self.process = subprocess.Popen(
                shlex.split(convert_cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        self._procs.append(self.process)

        final_output = myline = ''
        reader = io.TextIOWrapper(self.process.stdout, encoding='utf8')
        while True:
            out = reader.read(1)
            if out == '' and self.process.poll() is not None:
                break
            myline += out
            if out in ('\r', '\n'):
                m = re.search("Duration: ([0-9:.]+)", myline)
                if m:
                    try:
                        total = utils.duration_in_seconds(m.group(1))
                    except ValueError:
                        pass
                n = re.search("time=([0-9:]+)", myline)
                # time can be of format 'time=hh:mm:ss.ts' or 'time=ss.ts'
                # depending on ffmpeg version
                if n:
                    time = n.group(1)
                    if ':' in time:
                        time = utils.duration_in_seconds(time)
                    now_sec = int(float(time))
                    try:
                        self.nowQPBar.setValue(int(100 * now_sec / total))
                    except (UnboundLocalError, ZeroDivisionError):
                        pass
                self.update_text_edit_signal.emit(myline)
                final_output += myline
                myline = ''
        self.update_text_edit_signal.emit('\n\n')

        return_code = self.process.poll()

        log_data = {
                'command' : convert_cmd,
                'returncode' : return_code,
                'type' : 'VIDEO'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0

    def convert_image(self, from_file, to_file, size, mntaspect, imgcmd):
        """
        Convert an image using ImageMagick.
        Create conversion info ("cmd") and emit the corresponding signal
        in order an outputQTE to be updated with that info.
        Finally, save log information.

        Return True if conversion succeed, else False.
        """
        # note: from_file and to_file names are inside quotation marks
        use_wsl = self.parent.settings.value('use_wsl', type=bool)
        resize = ''
        if size:
            resize = '-resize {0}'.format(size)
            if not mntaspect:
                resize += '\!'

        imgcmd = ' ' + imgcmd.strip() + ' '
        command_name = utils.is_installed('magick', use_wsl)
        command, from_file, to_file = utils.wsl_adjust(use_wsl, command_name, from_file, to_file)
        cmd = f'{command} {from_file} {resize}{imgcmd}{to_file}'
        self.update_text_edit_signal.emit(cmd + '\n')
        child = subprocess.Popen(
                shlex.split(cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        self._procs.append(child)

        output = child.communicate()[0].decode('utf8', errors='replace')
        final_output = output
        self.update_text_edit_signal.emit(output+'\n\n')

        return_code = child.poll()

        log_data = {
                'command' : cmd,
                'returncode' : return_code,
                'type' : 'IMAGE'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0

    def convert_document(self, from_file, to_file, all_supported_conversions):
        """
        Create a libreoffice (soffice) headless command and run it.
        Also emits the signals for outputQTE to update.

        Return True if conversion succeed, else False.
        """
        # note: from_file and to_file names are inside quotation marks
        use_wsl = self.parent.settings.value('use_wsl', type=bool)
        from_file_ext = utils.get_extension(from_file, all_supported_conversions)
        to_file_ext = utils.get_extension(to_file, all_supported_conversions)
        filter_name = utils.get_document_filter(from_file_ext, to_file_ext)
        target = filter_name if filter_name else to_file_ext

        # libreoffice always derives the output name from the input file and
        # cannot write to arbitrary file names, so convert into a temporary
        # directory and move the result to the requested path afterwards.
        tmp_dir = os.path.join(config.tmp_dir, str(uuid.uuid4()))
        lo_profile = os.path.join(tmp_dir, 'profile')
        os.makedirs(tmp_dir, exist_ok=True)

        # soffice is treated as an alias of libreoffice, prefer it when present.
        lo_cmd = (self.parent.libreoffice or
                  utils.is_installed('soffice', use_wsl) or
                  utils.is_installed('libreoffice', use_wsl))
        force_unix = lo_cmd.startswith('wsl -- ')
        # keep the command as a single argument, the resolved path may contain
        # spaces (e.g. C:\Program Files\...)
        if force_unix:
            lo_args = ['wsl', '--', lo_cmd[7:]]
        else:
            lo_args = [lo_cmd]
        profile_uri = urljoin('file://',
                pathname2url(utils.wsl_path(lo_profile, force_unix, quote=False)))
        args = lo_args + [
                '--headless',
                '-env:UserInstallation=' + profile_uri,
                '--convert-to', target,
                utils.wsl_path(from_file, force_unix, quote=False),
                '--outdir', utils.wsl_path(tmp_dir, force_unix, quote=False),
                ]
        cmd = ' '.join(shlex.quote(part) for part in args)
        self.update_text_edit_signal.emit(cmd + '\n')

        final_output = ''
        return_code = 1
        timed_out = False
        child = None
        try:
            child = subprocess.Popen(
                    args,
                    stderr=subprocess.STDOUT,
                    stdout=subprocess.PIPE,
                    start_new_session=os.name != 'nt'
                    )
            self._procs.append(child)
            try:
                output = child.communicate(timeout=config.document_timeout)[0]
            except subprocess.TimeoutExpired:
                timed_out = True
                kill_process_tree(child)
                output = child.communicate()[0]
            final_output = output.decode('utf8', errors='replace')
            self.update_text_edit_signal.emit(final_output + '\n\n')
            return_code = child.poll()

            # move the produced file to the requested output path
            produced = [os.path.join(tmp_dir, f)
                        for f in os.listdir(tmp_dir)
                        if os.path.isfile(os.path.join(tmp_dir, f))]
            if return_code == 0 and not timed_out and produced:
                matching = [p for p in produced
                            if p.lower().endswith('.' + to_file_ext.lower())]
                if matching:
                    src = matching[0]
                    to_path = to_file.replace('"', '')
                    dest_dir = os.path.dirname(to_path)
                    if dest_dir:
                        os.makedirs(dest_dir, exist_ok=True)
                    if os.path.exists(to_path):
                        os.remove(to_path)
                    shutil.move(src, to_path)
                else:
                    # conversion produced some stray temp files, but failed
                    return_code = 1
            elif not timed_out:
                # no output file was produced
                return_code = 1
        finally:
            if child is not None and child in self._procs:
                self._procs.remove(child)
            shutil.rmtree(tmp_dir, ignore_errors=True)

        log_data = {
                'command' : cmd,
                'returncode' : return_code,
                'type' : 'DOCUMENT'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0

    def convert_markdown(self, from_file, to_file):
        """
        Use pandoc to convert markdown files.
        The syntax is 'pandoc -s <input> -o <output>'
        """
        use_wsl = self.parent.settings.value('use_wsl', type=bool)
        command, from_file, to_file = utils.wsl_adjust(use_wsl, 'pandoc', from_file, to_file)
        cmd = f'{command} -s {from_file} -o {to_file}'
        self.update_text_edit_signal.emit(cmd + '\n')
        child = subprocess.Popen(
                shlex.split(cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        self._procs.append(child)

        output = child.communicate()[0].decode('utf8', errors='replace')
        final_output = output
        self.update_text_edit_signal.emit(output+'\n\n')

        return_code = child.poll()

        log_data = {
                'command' : cmd,
                'returncode' : return_code,
                'type' : 'MARKDOWN'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0

    def convert_compression(self, from_file, to_file, all_supported_conversions):
        """
        Use tar/ar/squashfs-tools/(un)zip to convert compressed files.
        """
        from_file_ext = utils.get_extension(from_file, all_supported_conversions)
        to_file_ext = utils.get_extension(to_file, all_supported_conversions)
        use_wsl = self.parent.settings.value('use_wsl', type=bool)

        # Start by decompressing
        # use a unique subdir so we never touch a shared directory's contents
        # also create parent dirs (C:/temp may not exist on Windows)
        import uuid
        decompress_dir = os.path.join(config.tmp_dir, str(uuid.uuid4()))
        if to_file_ext == "[Folder]":
            decompress_dir = to_file.replace(".[Folder]","").replace("\"","")
            os.makedirs(decompress_dir, exist_ok=True)
        else:
            os.makedirs(decompress_dir)

        if from_file_ext in ['deb', 'a', 'ar', 'o', 'so']:
            command, cmd_from_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'ar', from_file, decompress_dir)
            cmd = f'{command} -x {cmd_from_file} --output {cmd_decompress_dir}'
        elif from_file_ext in ['sqfs', 'squashfs', 'snap']:
            command, cmd_from_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'unsquashfs', from_file, decompress_dir)
            cmd = f'{command} -d {cmd_decompress_dir} {cmd_from_file}'
        elif from_file_ext in ['zip']:
            command, cmd_from_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'unzip', from_file, decompress_dir)
            cmd = f'{command} {cmd_from_file} -d {cmd_decompress_dir}'
        else:
            command, cmd_from_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'tar', from_file, decompress_dir)
            cmd = f'{command} -xvf {cmd_from_file} -C {cmd_decompress_dir}'
        self.update_text_edit_signal.emit(cmd + '\n')
        child = subprocess.Popen(
                shlex.split(cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        self._procs.append(child)

        output = child.communicate()[0].decode('utf8', errors='replace')
        final_output = output
        self.update_text_edit_signal.emit(output+'\n\n')

        return_code = child.poll()

        log_data = {
                'command' : cmd,
                'returncode' : return_code,
                'type' : 'DECOMPRESS'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        if return_code != 0:
            shutil.rmtree(decompress_dir)
            return False
        # Now, recompress the files in decompress_dir
        if to_file_ext in ['ar', 'a']:
            # ar can only 'add' single files to archives. so iterate over all
            overall_success = True
            for fpath in Path(decompress_dir).rglob('*.*'):
                if os.path.isfile(fpath):
                    command, to_file, fpath = utils.wsl_adjust(use_wsl, 'ar', to_file, str(fpath))
                    cmd = f'{command} r {to_file} \"{fpath}\"'
                    self.update_text_edit_signal.emit(cmd + '\n')
                    child = subprocess.Popen(
                            shlex.split(cmd),
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE
                            )
                    self._procs.append(child)

                    output = child.communicate()[0].decode('utf8', errors='replace')
                    final_output = output
                    self.update_text_edit_signal.emit(output+'\n\n')

                    return_code = child.poll()
                    if return_code != 0:
                        overall_success = False

                    log_data = {
                            'command' : cmd,
                            'returncode' : return_code,
                            'type' : 'DECOMPRESS'
                            }
                    log_lvl = logging.info if return_code==0 else logging.error
                    log_lvl(final_output, extra=log_data)
            shutil.rmtree(decompress_dir)
            return overall_success
        elif to_file_ext in ['sqfs', 'squashfs']:
            command, cmd_to_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'mksquashfs', to_file, decompress_dir)
            cmd = f'{command} {cmd_decompress_dir} {cmd_to_file}'
        elif to_file_ext in ['tgz', 'tar.gz']:
            command, cmd_to_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'tar', to_file, decompress_dir)
            cmd = f'{command} -czvf {cmd_to_file} --directory={cmd_decompress_dir} .'
        elif to_file_ext in ['zip']:
            command, cmd_to_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'zip', to_file, decompress_dir)
            cmd = f'{command} -r -q {cmd_to_file} {cmd_decompress_dir}'
        elif to_file_ext in ['tar']:
            command, cmd_to_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'tar', to_file, decompress_dir)
            cmd = f'{command} -cvf {cmd_to_file} --directory={cmd_decompress_dir} .'
        elif to_file_ext in ['[Folder]']:
            # nothing to do, decompress was enough
            return True
        elif to_file_ext in ['tar.bz2']:
            command, cmd_to_file, cmd_decompress_dir = utils.wsl_adjust(use_wsl, 'tar', to_file, decompress_dir)
            cmd = f'{command} -cvjSf {cmd_to_file} --directory={cmd_decompress_dir} .'

        self.update_text_edit_signal.emit(cmd + '\n')
        child = subprocess.Popen(
                shlex.split(cmd),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        self._procs.append(child)

        output = child.communicate()[0].decode('utf8', errors='replace')
        final_output = output
        self.update_text_edit_signal.emit(output+'\n\n')

        return_code = child.poll()

        log_data = {
                'command' : cmd,
                'returncode' : return_code,
                'type' : 'DECOMPRESS'
                }
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        shutil.rmtree(decompress_dir)
        return return_code == 0

    def convert_model(self, from_file, to_file, all_supported_conversions):
        # can't be imported at the start because its a optional dependency
        import trimesh
        # python library doesn't need escaped paths, we can undo that
        from_file = from_file.replace('"', '').replace('\\', '')
        to_file   =   to_file.replace('"', '').replace('\\', '')
        
        # these formats require gmsh in addition to trimesh
        needs_gmsh = utils.get_extension(from_file, all_supported_conversions) in ['brep', 'step', 'iges', 'inp', 'bdf'] or utils.get_extension(to_file, all_supported_conversions) in ['inp', 'bdf']
        # check that GMSH is installed, append to sys.path if needed
        if needs_gmsh and not utils.is_installed('gmsh', False, is_import=True):
            self.update_text_edit_signal.emit("Would fail to load GMSH, retrying with /usr/local/lib\n")
            if not '/usr/local/lib' in sys.path:
                sys.path.append('/usr/local/lib')
            # retry with the new sys.path
            if not utils.is_installed('gmsh', False, is_import=True):
                self.update_text_edit_signal.emit("Unable to locate GMSH, please install it. (using PyPi/pip)\n")
                return False

        try:
            if needs_gmsh:
                self.update_text_edit_signal.emit(f"Loading file from {from_file} using trimesh.gmsh\n")
                mesh = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(file_name=from_file))
            else:
                self.update_text_edit_signal.emit(f"Loading file from {from_file} using trimesh.default\n")
                mesh = trimesh.load(from_file)
            self.update_text_edit_signal.emit(f"Saving File to {to_file}\n")
            mesh.export(to_file)
        except Exception as e:
            self.update_text_edit_signal.emit(f"Failed: {e}\n")
            return False
        return True

    def convert_dynamic(self, from_file, to_file, converter, all_supported_conversions):
        if converter == "ffmpeg":
            return self.convert_video(from_file, to_file, "")
        elif converter == "pandoc":
            return self.convert_markdown(from_file, to_file)
        elif converter == "magick":
            return self.convert_image(from_file, to_file, "", "", "")
        elif converter == "soffice":
            return self.convert_document(from_file, to_file, all_supported_conversions)
        elif converter == "compression":
            return self.convert_compression(from_file, to_file, all_supported_conversions)
        elif converter == "trimesh":
            return self.convert_model(from_file, to_file, all_supported_conversions)
        elif converter == "unsupported":
            print("Error: Did not find suitable converter for dynamic conversion!")
        else:
            print(f"Error: Found converter \"{converter}\", but it does not implement conversion yet!")
        return False
