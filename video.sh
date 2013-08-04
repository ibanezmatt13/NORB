#!/bin/bash
 
while [ 1 ]; do # do forever
{
raspivid -w 1920 -h 1080 -n -o /home/pi/`date +%H%M%S` -t 300000 # executing recording with some parameters
sleep 1 # delay for one second
}
 
done
