#!/bin/bash

function reinstall {
    sudo pip uninstall ffmulticonverter --break-system-packages
    sudo pip install . --break-system-packages
}

if [[ -z "${REINSTALL_NOCONFIRM}" ]]; then
    echo "This script is used for reinstalling the program from this source."
    echo "This is used for testing changes in the source code."
    echo "If you instead wanted to install/uninstall:"
    echo "Install: 'sudo pip install ."
    echo "Uninstall: 'sudo pip uninstall ffmulticonverter'"
    echo "Suppress this Warning: set $REINSTALL_NOCONFIRM to anything"
    echo ""
    read -p "Do you want to reinstall? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        reinstall
    fi
    exit
else
    reinstall
fi