#### What is this?  
This is a fork of the original https://github.com/ilstam/FF-Multi-Converter.  
The original is [no longer developed](https://github.com/ilstam/FF-Multi-Converter/issues/61#issuecomment-467869122).  
  
This program is a simple graphical application which enables you to convert  
between all popular formats, by utilizing and combining other programs.  
To simply convert files, just click the Add button, add your file(s) and  
select a format in the dropdown list, then click Convert.  
For Videos, Music and Images, there are additional  
options, for example flipping the image or selecting codecs, in the tabs.  

Both Linux and Windows are supported and tested.  
MacOS should work, but I don't have a Mac, so I can't test that.

#### Dependencies:
* python3  
* pyqt5  

#### Optional dependencies:
(Without these some conversions will not work)  

* ffmpeg (Audio and Video)  
* imagemagick (Images)  
* unoconv (Office formats)  
* pandoc (Markdown)  
* squashfs-tools, zip, unzip, binutils, tar, gzip, bzip2 (Compressed files)  

#### Installation
Install the `ffconverter` package from PyPI.  
`pip` works on Windows and most Linux Distributions.  

```sh
pip install ffconverter
```

#### Troubleshooting (Linux)
On some distros (externally managed environments, Arch, Debian),  
`pip` will not work. In this case, you should use `pipx`.  

```sh
sudo PIPX_HOME=/usr/local/pipx PIPX_BIN_DIR=/usr/local/bin pipx install --system-site-packages ffconverter
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/applications/ffconverter.desktop /usr/local/share/applications/ffconverter.desktop
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/pixmaps/ffconverter.png /usr/local/share/icons/ffconverter.png
```

The last two commands are needed to add the program to your installed  
applications, but the `ffconverter` command should be available without them.  

#### Troubleshooting (Windows)

If you use Windows, you will likely not have any of the programs  
the converter uses. You will need to install them by either manually putting  
.exe files on your PATH or (recommended) by using [scoop](https://scoop.sh).  
If the programs are not available after that, close your CMD.  

If you want the program on your Desktop, create a new Shortcut  
and enter this as the path:  

```sh
"C:\Program Files\Python310\pythonw.exe" -c "from ffconverter import ffconverter as ff; ff.main()"
```

You may need to replace the path to pythonw.exe with the correct path  
for your system. You can get this path by running this CMD Command:  

```sh
where pythonw
```

#### Uninstall
Simply run:  
```sh
pip uninstall ffconverter
```
Adjust this command if you used something other than `pip` to install.  

#### Run without installing
You can launch the application without installing it  
by running the launcher script:  

```sh
git clone https://github.com/l-koehler/ff-converter
cd ./ff-converter
python3 ./launcher
```
