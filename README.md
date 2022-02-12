# pyLocateMAC

This project allows the network administrator to locate a MAC address within the 
managed network. It checks the SNMP MAC address table of every managed switch in 
order to find the corresponding port for that MAC address.

## Why? 
Sometimes I have to locate devices within the network in my job. In the 
past I used a crude BASH script for that. It worked okay-ish but I wanted to learn 
how to work with SNMP in Python.

Sure, there are most likely better ways to solve this issue. Surely easier ways 
but where would be the fun in that? Right.

## What is next? 
When the general functionality is implemented I will frame this with a Flask 
web page. This will allow me to put this script in a docker container or a 
small vm. But this is will happen in a later stage. Much much later ... 