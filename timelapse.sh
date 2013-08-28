#!/bin/bash
 
while [ 1 ]; do # do forever
{
raspistill -o images/image/`date +"%Y%m%d%H%M"` + ".jpg"
sleep 30 # delay for one second
}
 
done
