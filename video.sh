#!/bin/bash
 
while [ 1 ]; do # do forever
{
raspivid -w 1280 -h 720 -n -o /home/pi/`date +%H%M%S` -t 300000 # executing recording with some parameters
sleep 1 # delay for one second
}
 
done
