#!/bin/bash

while [ 1 ] do # do  forever
{
/home/pi/NORB.py & # execute the main tracker executable
sleep 1 # delay for one second
}

done
