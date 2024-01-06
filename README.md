#### What is this?  
This is a fork of the original https://github.com/ilstam/FF-Multi-Converter.  
The original is [no longer developed](https://github.com/ilstam/FF-Multi-Converter/issues/61#issuecomment-467869122).  
  
This program is a simple graphical application which enables you to convert  
between all popular formats, by utilizing and combining other programs.  
To simply convert files, just click the Add button, add your file(s) and  
select a format in the dropdown list, then click Convert.  
For Videos, Music and Images, there are additional  
options, for example flipping the image or selecting codecs, in the tabs.  

#### Dependencies:
* python3  
* pyqt5  

#### Optional dependencies:
(Without these some conversions will not work)  

* ffmpeg (Audio and Video)  
* imagemagick (Images)  
* unoconv (Office formats)  
* pandoc (Markdown)  
* tar, ar, squashfs-tools, zip (Compressed files)  

#### Installation
Install the `ffconverter` package from PyPI.  
`pip` works on most distros and should be the simplest choice.

```sh
pip install ffconverter
```

#### Troubleshooting
On some distros (externally managed environments, Arch, Debian),  
`pip` will not work. In this case, you should use `pipx`.  

```sh
sudo PIPX_HOME=/usr/local/pipx PIPX_BIN_DIR=/usr/local/bin pipx install --system-site-packages ffconverter
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/applications/ffconverter.desktop /usr/local/share/applications/ffconverter.desktop
sudo ln -sf /usr/local/pipx/venvs/ffconverter/share/pixmaps/ffconverter.png /usr/local/share/icons/ffconverter.png
```

The last two commands are needed to add the program to your installed  
applications, but the `ffconverter` command should be available without them.  

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
