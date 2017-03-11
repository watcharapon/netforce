#!/bin/bash
for mod in netforce*; do
    echo "installing $mod..."
    cd $mod
    rm -rf build dist
    cd ..
done
