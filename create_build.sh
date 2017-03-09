#!/bin/bash
for mod in netforce*; do
    echo "installing $mod..."
    cd $mod
    folder=${PWD##*/}
    #rm MANIFEST.in
    echo "recursive-include "$folder" *" > MANIFEST.in
    ./setup.py bdist_egg
    rm MANIFEST.in
    cd ..
done
[ -d foo ] || mkdir dist
cp build_egg.sh dist/
find . -name '*.egg' -print0 | xargs -0 -I {} mv {} dist
