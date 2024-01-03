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
```
In some cases, the program might not appear in your installed applications, but  
the `ffconverter` command will be available. In this case, run:
```sh
wget https://raw.githubusercontent.com/l-koehler/FF-converter/master/share/ffconverter.desktop -O ~/.local/share/applications/ffconverter.desktop
```
This command should add ffconverter to your installed applications, so you can  
access the program without the terminal.

#### Uninstall
Simply run:  
```sh
pip uninstall ffmulticonverter
```
Adjust this command if you used something other than `pip` to install.  

#### Run without installing
You can launch the application without installing it  
by running the launcher script:  
```sh
python3 launcher
```