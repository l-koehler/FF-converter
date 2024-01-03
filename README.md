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
Install the 'ffconverter' package from PyPI.
You can use 'pip' for that, but if using Debian or Arch (or if you prefer isolated packages in general), you
should use 'pipx'.
```sh
pipx install ffconverter
```


#### Uninstall
From this directory:  
```sh
sudo pip uninstall ffmulticonverter
```

#### Run without installing
You can launch the application without installing it  
by running the launcher script:  
```sh
python3 launcher
```