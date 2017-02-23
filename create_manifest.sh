#!/bin/bash
for mod in netforce*; do
    echo "installing $mod..."
    cd $mod
    folder=${PWD##*/}
    #rm MANIFEST.in
    echo "recursive-include "$folder" *" > MANIFEST.in
    ./setup.py develop
    cd ..
done
