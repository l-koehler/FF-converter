#### What is this?  
This is a fork of the original https://github.com/ilstam/FF-Multi-Converter.  
The original is [no longer developed](https://github.com/ilstam/FF-Multi-Converter/issues/61#issuecomment-467869122).  
  
This program is a simple graphical application which enables you to convert  
between most popular file formats, by utilizing and combining other programs.  
To simply convert files, just click the Add button, add your file(s) and  
select a format in the dropdown list, then click Convert.  
For Videos, Music and Images, there are additional  
options, for example flipping the image or selecting codecs, in the tabs.  

Both Linux and Windows are supported and tested.  
MacOS should work, but I can't test that.  

#### Dependencies:
* python3 (3.9 or newer)  
* pyqt5  

On Linux, use your distributions package manager or pip to install these.  
On Windows, use [python.org](https://python.org) to get python (the version  
in the Microsoft Store is [worse in some regards](https://docs.python.org/3/using/windows.html#known-issues)), then use  
`python -m pip install PyQt5` to get PyQt5.  

#### Optional dependencies:
Without these some conversions will not work.  

Python packages:  

* trimesh (python package, used for 3D Models)  
* gmsh (python package, requires trimesh, used for more 3D Models)  

Install them with the `models` extra:  

```sh
pip install "ffconverter[models]"
```

`gmsh` publishes prebuilt wheels only for x86-64 Linux/macOS, ARM macOS  
and Windows x64 (on Linux the wheel additionally needs a recent enough  
glibc). On platforms without a wheel (notably Linux ARM) it is skipped  
automatically; if you need gmsh-backed conversions there, build it  
manually, see the ARM section below.  

System Packages:  

* ffmpeg (Audio and Video)  
* imagemagick (Images)  
* unoconv (Office formats)  
* pandoc (Markdown)  
* squashfs-tools, zip, unzip, binutils, tar, gzip, bzip2 (Compressed files)  

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

If you need 3D model conversion, install the optional Python dependencies
as well:

```sh
pip install "ffconverter[models]"
```

#### Troubleshooting
If a optional dependency is installed after the program, you might  
need to restart the program twice to ensure the cache gets overwritten.  
If this does not work, delete the cache (Preferences -> Delete Cache).  

#### Troubleshooting (Linux ARM CPUs)
For converting 3D Models, the python packages `trimesh` and `gmsh` are  
required. `gmsh` has no prebuilt wheel for Linux ARM, so the `models`  
extra installs `trimesh` only there. You can compile `gmsh` yourself using the script below.  
Compiling this might take a while, depending on your device.  
```bash
git clone https://gitlab.onelab.info/gmsh/gmsh.git # 200+ MiB size
mkdir ./gmsh/build
cd ./gmsh/build

# You can probably replace `gcc` and `g++` with any other C/C++ Compiler.
CC=gcc CXX=g++ cmake -DENABLE_BUILD_DYNAMIC=1 ..
make
sudo make install

# optional, you no longer need the git repo
cd ../..
rm -r ./gmsh
```

#### Troubleshooting (Linux)
On some distros ("externally managed environments", like Arch and Debian),  
`pip` will not work. In this case, you should use `pipx`.  

```sh
sudo PIPX_HOME=/usr/local/pipx PIPX_BIN_DIR=/usr/local/bin pipx install --system-site-packages ffconverter
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/applications/ffconverter.desktop /usr/local/share/applications/ffconverter.desktop
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/pixmaps/ffconverter.png /usr/local/share/pixmaps/ffconverter.png
```

`pip` places the `.desktop` file, icon and man page inside the environment's  
`share/` directory (`.../venvs/ffconverter/share/`). The last two commands  
link them into the system-wide locations so the program appears in your  
application menu, but the `ffconverter` command works without them.  
`pipx` does not integrate desktop menus on its own.  

#### Troubleshooting (Windows)
The `ffconverter` command is installed as a windowed launcher, so no console  
window appears. If you want the program on your Desktop, create a new  
Shortcut and use the launcher's path (run `where ffconverter` to get it).  
Wrap the printed path in quotes if it contains spaces.  

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
