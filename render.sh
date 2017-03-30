#! /bin/bash

cat $1 | python footnote.py | \
    sed -e 's/!C/<font color=green>\&clubs;<\/font>/g' \
	-e 's/!D/<font color=orange>\&diams;<\/font>/g' \
	-e 's/!H/<font color=red>\&hearts;<\/font>/g' \
	-e 's/!S/<font color=blue>\&spades;<\/font>/g' \
	-e 's/!N/N/g' \
	-e 's/--/\&ndash;/g' \
    | perl markdown.pl | cat base.html - 
