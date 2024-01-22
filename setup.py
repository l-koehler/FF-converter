#!/usr/bin/env python3

import ffconverter
from distutils.core import setup
import os

if os.name == 'nt':
    data_files = [('share/applications', ['share/ffconverter.desktop']),
                ('share/pixmaps', ['share/ffconverter.png']),
                ('share/ffconverter', ['share/presets.xml']),
                ('share/man/man1', ['man/ffconverter.1.gz'])]
else:
    data_files = [('share/applications/', ['share/ffconverter.desktop']),
                ('share/pixmaps/', ['share/ffconverter.png']),
                ('share/ffconverter', ['share/presets.xml']),
                ('share/man/man1', ['man/ffconverter.1.gz'])]

setup(
    name = ffconverter.__name__,
    packages = [ffconverter.__name__],
    scripts = ['bin/ffconverter'],
    data_files = data_files,
    version = ffconverter.__version__,
    description = ffconverter.__description__,
    author = ffconverter.__author__,
    author_email = ffconverter.__author_email__,
    maintainer = ffconverter.__maintainer__,
    maintainer_email = ffconverter.__maintainer_email__,
    license = ffconverter.__license__,
    platforms = ffconverter.__platforms__,
    url = ffconverter.__url__,
    keywords = ['convert', 'file format', 'extension', 'audio', 'video',
                'images', 'documents', 'ffmpeg', 'imagemagick', 'unoconv',
                'pandoc'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Natural Language :: Bulgarian',
        'Natural Language :: Catalan',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Czech',
        'Natural Language :: French',
        'Natural Language :: Italian',
        'Natural Language :: Galician',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Hungarian',
        'Natural Language :: Malay',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Romanian',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
        'Natural Language :: Turkish',
        'Natural Language :: Vietnamese',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Utilities'],
    long_description = """
FF Converter
-------------------

Graphical application which enables you to convert audio, video, image and
document files between all popular formats using ffmpeg, unoconv, and ImageMagick.

Features:
 - Conversions for several file formats.
 - Very easy to use interface.
 - Access to common conversion options.
 - Audio/video ffmpeg-presets management.
 - Options for saving and naming files.
 - Multilingual - over 20 languages.

Requires: python3, pyqt5
Optionally requires: ffmpeg, imagemagick, unoconv, pandoc, tar, ar, zip, squashfs-tools
"""
)
