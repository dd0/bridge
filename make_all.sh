#! /bin/sh

for i in $(find ./src/ -name \*.md); do
    ./render.sh $i > docs/$(basename -s .md $i).html
done
