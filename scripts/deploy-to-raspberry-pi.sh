#!/bin/bash

backups_directory="escape-server-backups"

echo "1. Backing up current 'escape-server' directory on rasperry pi..."
sshpass -p 'raspberry' ssh pi@raspberrypi.local "
mkdir -p $backups_directory;
tar -czf $backups_directory/\$(date +%F_%H-%M-%S).tar.gz escape-server;
"

echo "2. Delete current 'escape-server' directory on raspberry pi..."
sshpass -p 'raspberry' ssh pi@raspberrypi.local "
sudo rm -rf escape-server;"

current_git_directory=`git rev-parse --show-toplevel`

echo "3. Copying current git respository to rasperry pi..."
sshpass -p 'raspberry' scp -r $current_git_directory pi@raspberrypi.local:/home/pi

echo "DONE"
