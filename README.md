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

On Linux, use your distributions package manager or pip to install these.  
On Windows, use [python.org](https://python.org) to get python (the version  
in the Microsoft Store is [worse in some regards](https://docs.python.org/3/using/windows.html#known-issues)), then use  
`python -m pip install PyQt5` to get PyQt5.  

#### Optional dependencies:
Without these some conversions will not work.  

System Packages:  

* ffmpeg (Audio and Video)  
* imagemagick (Images)  
* unoconv (Office formats)  
* pandoc (Markdown)  
* squashfs-tools, zip, unzip, binutils, tar, gzip, bzip2 (Compressed files)  

Python packages:  

* trimesh _AND_ gmsh (python packages, used for 3D Models)  

These should be installed automatically when using pip/pipx,  
but if you don't need to convert 3D Models you can remove these.  

On Linux, use your distributions Package manager to install the System  
packages. On Windows, either get .exe files and place them on the $PATH,  
use [scoop](https://scoop.sh), or (for everything but ffmpeg) install the  
dependencies in WSL. You could also try other third-party package managers  
or even the Microsoft Store, the program only needs the command  
(e.g. `unoconv`) to be available on the CMD.  

#### Installation
Install the `ffconverter` package from PyPI.  
`pip` works on Windows and most Linux Distributions.  

```sh
pip install ffconverter
```

#### Troubleshooting
If a optional dependency is installed after the program, you might  
need to restart the program twice to ensure the cache gets overwritten.  
If this does not work, delete the cache (Preferences -> Delete Cache).  

#### Troubleshooting (Linux)
On some distros ("externally managed environments", like Arch and Debian),  
`pip` will not work. In this case, you should use `pipx`.  

```sh
sudo PIPX_HOME=/usr/local/pipx PIPX_BIN_DIR=/usr/local/bin pipx install --system-site-packages ffconverter
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/applications/ffconverter.desktop /usr/local/share/applications/ffconverter.desktop
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/pixmaps/ffconverter.png /usr/local/share/icons/ffconverter.png
```

The last two commands are needed to add the program to your installed  
applications, but the `ffconverter` command should be available without them.  

#### Troubleshooting (Windows)
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
