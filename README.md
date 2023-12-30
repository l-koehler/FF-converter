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
From this directory:  
```sh
sudo pip install .
```  
Arch Linux will complain that the system is externally managed, bypass  
this by passing --break-system-packages.  
pip will also complain about sudo, but it doesn't work properly without it.  

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