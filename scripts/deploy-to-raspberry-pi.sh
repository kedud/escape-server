#!/bin/bash

BACKUPS_DIRECTORY="escape-server-backups"
RASPBERRYPI_PASSWORD="raspberry"

echo "1/3. Backing up current 'escape-server' directory on rasperry pi..."
sshpass -p $RASPBERRYPI_PASSWORD ssh pi@raspberrypi.local "
mkdir -p $BACKUPS_DIRECTORY;
tar -czf $BACKUPS_DIRECTORY/\$(date +%F_%Hh%Mm%Ss).tar.gz escape-server;
"

echo "2/3. Delete current 'escape-server' directory on raspberry pi..."
sshpass -p $RASPBERRYPI_PASSWORD ssh pi@raspberrypi.local "
sudo rm -rf escape-server;"

CURRENT_GIT_DIRECTORY=`git rev-parse --show-toplevel`

echo "3/3. Copying current git respository to rasperry pi..."
sshpass -p $RASPBERRYPI_PASSWORD scp -r $CURRENT_GIT_DIRECTORY pi@raspberrypi.local:/home/pi

echo "DONE"
