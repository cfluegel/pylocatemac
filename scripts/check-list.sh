#!/bin/bash
# 

LISTE=$1

( while read line; do 
	IFS='|' read -a RESULT <<< $line 

        ping -W1 -q -n -c1 ${RESULT[1]} &> /dev/null
	[ $? -eq 1 ] && continue

	echo -n "${RESULT[1]}: "

	cd .. 
	python3 locate.py ${RESULT[0]} 
done ) < $LISTE

