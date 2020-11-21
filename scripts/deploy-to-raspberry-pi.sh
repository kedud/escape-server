#!/bin/bash

backups_directory="escape-server-backups"

echo "Make a backup of current 'escape-server' directory"
sshpass -p 'raspberry' ssh pi@raspberrypi.local "
mkdir -p $backups_directory;
tar -czf $backups_directory/\$(date +%F_%H-%M-%S).tar.gz escape-server;
"

echo "Delete current 'escape-server' directory on raspberry pi"
sshpass -p 'raspberry' ssh pi@raspberrypi.local "
sudo rm -rf escape-server;"

current_git_directory=`git rev-parse --show-toplevel`

echo "Copy Current git respository to rasperry pi"
sshpass -p 'raspberry' scp -r $current_git_directory pi@raspberrypi.local:/home/pi
