#!/bin/bash
 
while [ 1 ]; do
{
raspivid -w 1920 -h 1080 -n -o /home/pi/`date +%H%M%S` -t 300000
sleep 1
}
 
done
