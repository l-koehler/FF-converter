#### What is this?  
This is a fork of the original https://github.com/ilstam/FF-Multi-Converter.  
The original is [no longer developed](https://github.com/ilstam/FF-Multi-Converter/issues/61#issuecomment-467869122).  
  
This program is a simple graphical application which enables you to convert  
between all popular formats, by utilizing and combining other programs.  
These programs are optional dependencies, as some conversions will not work  
without them.  

#### Dependencies:
python3  
pyqt5  

#### Optional dependencies:
ffmpeg (Audio and Video)  
imagemagick (Images)  
unoconv (Office formats)  
pandoc (Markdown)  

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