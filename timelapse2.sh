#!/bin/bash
 
while [ 1 ]; do # do forever
{
DATE=$(date +"%Y%m%d%H%M")
raspistill -o images/image/ + date + ".jpg"
sleep 30 # delay for one second
}
 
done
