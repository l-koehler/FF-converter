import os
from ffconverter import utils

#-----general data

if os.name == 'nt':
    home = os.environ['USERPROFILE']
    config_dir = os.path.join(home, 'AppData/Local/ffconverter/').replace("\\", "/")
    tmp_dir = 'C:/temp/ffconverter'
else:
    home = os.getenv("HOME")
    config_dir = os.path.join(home, '.config/ffconverter/')
    tmp_dir = '/tmp/ffconverter/'

default_ffmpeg_cmd = ''
default_imagemagick_cmd = ''

#-----log/cache data

log_dir = os.path.join(config_dir, 'logs/').replace("\\", "/")
log_file = os.path.join(log_dir, 'history.log')
log_format  = '%(asctime)s : %(levelname)s - %(type)s\n' +\
              'Command: %(command)s\n' +\
              'Return code: %(returncode)s\n%(message)s\n'
log_dateformat = '%Y-%m-%d %H:%M:%S'
cache_dir = os.path.join(config_dir, 'cache/').replace("\\", "/")
cache_file = os.path.join(cache_dir, 'cache.ini')

#-----presets data

presets_file_name = 'presets.xml'
presets_file = os.path.join(config_dir, presets_file_name).replace("\\", "/")
presets_lookup_dirs = ["/usr/local/share/", "/usr/share/"]
presets_lookup_virtenv = 'share'
# prefix for old presets when synchronizing
presets_old = '__OLD'

#-----audiovideo data

video_codecs = [
        'copy', 'flv', 'h263', 'libvpx', 'libx264', 'libxvid', 'mpeg2video',
        'mpeg4', 'msmpeg4', 'wmv2'
        ]

audio_codecs = [
        'aac', 'ac3', 'copy', 'libfaac', 'libmp3lame', 'libvo_aacenc',
        'libvorbis', 'mp2', 'wmav2', 'opus'
        ]

video_formats = [
        '3g2', '3gp', 'aac', 'ac3', 'avi', 'dv', 'flac', 'flv', 'm4a', 'm4v',
        'mka', 'mkv', 'mov', 'mp3', 'mp4', 'mpg', 'ogg', 'vob', 'wav', 'webm',
        'wma', 'wmv'
        ]

video_frequency_values = [
        '22050', '44100', '48000'
        ]

video_bitrate_values = [
        '32', '96', '112', '128', '160', '192', '256', '320'
        ]

#-----image data

image_formats = [
        'avif', 'bmp', 'cgm', 'dpx', 'emf', 'eps', 'fpx', 'gif', 'jbig', 'jng', 'jpeg',
        'mrsid', 'p7', 'pdf', 'picon', 'png', 'ppm', 'psd', 'rad', 'tga',
        'tif','webp', 'xpm'
        ]

image_extra_formats = [
        'bmp2', 'bmp3', 'dib', 'epdf', 'epi', 'eps2', 'eps3', 'epsf', 'epsi',
        'icon', 'jpe', 'jpg', 'pgm', 'png24', 'png32', 'pnm', 'ps', 'ps2',
        'ps3', 'sid', 'tiff'
        ]

image_common_formats = [
        'bmp', 'eps', 'gif', 'jpeg', 'jpg', 'pdf', 'png', 'tif', 'tiff', 'webp',
        'ico'
        ]

#-----document data

document_formats = [
        'bib', 'csv', 'dif', 'doc', 'docx', 'html', 'ltx', 'odp', 'ods', 'odt',
        'pdf', 'ppt', 'pptx', 'rtf', 'sdc', 'sdw', 'txt', 'xls', 'xlsx', 'xml'
        ]

# timeout (seconds) for a single libreoffice/soffice invocation
document_timeout = 120

# Which document category an input extension belongs to.
# LibreOffice's export filters depend on the type it picked on import (Calc/Draw/Impress/Writer),
# so the category is needed to select the correct filter for an output.
document_input_categories = {
        # spreadsheets (Libreoffice Calc)
        'csv': 'calc', 'xls': 'calc', 'xml': 'calc', 'xlsx': 'calc',
        'ods': 'calc', 'sdc': 'calc',
        # drawings/images (and PDFs for some reason) (Draw)
        'eps': 'img', 'emf': 'img', 'gif': 'img', 'jpg': 'img', 'odg': 'img',
        'png': 'img', 'tiff': 'img', 'bmp': 'img', 'webp': 'img',
        'pdf': 'img',
        # presentations (Impress)
        'odp': 'slide', 'ppt': 'slide', 'pptx': 'slide', 'sda': 'slide',
        # word processing (Writer)
        'html': 'text', 'doc': 'text', 'docx': 'text', 'odt': 'text',
        'txt': 'text', 'rtf': 'text', 'sdw': 'text',
        }

# Explicit export filters, per input category and output extension.
# Only targets that would otherwise fail to find a filter need an entry,
# everything else falls back to "--convert-to <ext>"
# See https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html
document_filters = {
        'calc': {
            'csv':  'csv:Text - txt - csv (StarCalc):44,34,76,1',
            'html': 'html:HTML (StarCalc)',
            'xlsx': 'xlsx:Calc Office Open XML',
            },
        'img': {},
        'slide': {
            'html': 'html:impress_html_Export',
            'pptx': 'pptx:Impress MS PowerPoint 2007 XML',
            },
        'text': {
            'doc':  'doc:MS Word 97',
            'docx': 'docx:MS Word 2007 XML',
            'html': 'html:HTML (StarWriter)',
            'odt':  'odt:writer8',
            'rtf':  'rtf:Rich Text Format',
            'xml':  'xml:MS Word 2003 XML',
            },
        }

#-----markdown data

markdown_formats = [
        'adoc', 'bib', 'bibtex', 'docbook', 'docbook4', 'docbook5', 'docx',
        'dokuwiki', 'epub', 'epub2', 'epub3', 'fb2', 'gfm', 'haddock', 'html',
        'html4', 'html5', 'icml', 'ipynb', 'jats', 'jira', 'json', 'ltx',
        'man', 'md', 'markua', 'mediawiki', 'ms', 'muse', 'native', 'odt',
        'odf', 'opml', 'org', 'pdf', 'txt', 'pptx', 'rst', 'rtf', 'tei',
        'texinfo', 'textile', 'typst', 'xwiki', 'zim'
    ]
common_markdown_formats = ['docx', 'dokuwiki', 'epub', 'epub2', 'epub3', 'html',
                           'ipynb', 'json', 'ltx', 'man', 'md', 'odt', 'odf',
                           'txt', 'pptx', 'rtf']

#-----compression data

compression_formats = [
        '[Folder]', 'ar', 'squashfs', 'tar', 'tgz', 'zip'
    ]

common_compression_formats = [
        '[Folder]', 'tar', 'tar.gz', 'zip'
        ]

#-----common formats (used for not displaying uncommon formats)
common_formats = image_common_formats + document_formats + common_markdown_formats + video_formats + common_compression_formats

#-----misc
translators = [
        ['[bg] Bulgarian', 'Vasil Blagoev'],
        ['[ca] Catalan', 'David Sabadell i Ximenes'
                  '\n     Toni Estévez'],
        ['[cs] Czech', 'Petr Simacek'],
        ['[de_DE] German (Germany)', 'Stefan Wilhelm'
                              '\n     l-koehler'],
        ['[el] Greek', 'Ilias Stamatis'],
        ['[es] Spanish', 'Miguel Ángel Rodríguez Muíños'
                  '\n     Toni Estévez'],
        ['[fr] French', 'Rémi Mercier'
                 '\n     Lebarhon'],
        ['[gl] Galician', 'Miguel Anxo Bouzada'],
        ['[gl_ES] Galician (Spain)', 'Miguel Anxo Bouzada'],
        ['[hu] Hungarian', 'Farkas Norbert'],
        ['[it] Italian', 'Fabio Boccaletti'],
        ['[ms_MY] Malay (Malaysia)', 'abuyop'],
        ['[pl_PL] Polish (Poland)', 'Lukasz Koszy'
                             '\n     Piotr Surdacki'],
        ['[pt] Portuguese', 'Sérgio Marques'
                     '\n     Paulo Braz'
                     '\n     Nuno Duarte'],
        ['[pt_BR] Portuguese (Brasil)', 'José Humberto A Melo'],
        ['[ro_RO] Romanian (Romania)', 'Angelescu Constantin'],
        ['[ru] Russian', 'Andrew Lapshin'],
        ['[tu] Turkish', 'Tayfun Kayha'],
        ['[vi] Vietnamese', 'Anh Phan'],
        ['[zh_CN] Chinese (China)', 'Dianjin Wang'
                             '\n     Ziyun Lin'],
        ['[zh_TW] Chinese (Taiwan)', 'Taijuin Lee'
                              '\n     Jeff Huang'],
        ]
