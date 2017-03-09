#!/bin/bash
for mod in netforce*; do
    echo "installing $mod..."
    easy_install $mod 
done
