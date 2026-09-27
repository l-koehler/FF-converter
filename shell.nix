{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pyqt5
    ffmpeg
    imagemagick
    pandoc
    zip
    unzip
    gnutar
    gzip
    bzip2
    squashfsTools
    binutils
    python3Packages.trimesh
    python3Packages.pytest
    python3Packages.build
    qt5.qtbase
    # optional, needed for some document stuff
    # libreoffice unoconv
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [
      pkgs.python3Packages.pyqt5
      pkgs.libGL
      pkgs.glib
    ]};
    # PyQt5 wheel-style layout doesn't bundle platform plugins, point at qtbase
    export QT_QPA_PLATFORM_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms
  '';
}
