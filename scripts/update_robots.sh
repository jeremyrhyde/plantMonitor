#!/bin/bash

update_command="
  sudo systemctl stop gardener.service;
  sudo systemctl disable api.service;
  sudo systemctl disable robot.service;

  sudo systemctl stop gardener.service;
  sudo systemctl stop robot.service;
  sudo systemctl stop api.service;

  echo 'Resetting log file';

  rm -f /home/pi/temp.log;
  touch /home/pi/temp.log

  echo 'Starting git update...';

  cd /home/pi/plantmonitor/;
  git pull;
  git reset --hard origin/master_dev;

  echo 'Finished pulling from git';

  sudo cp /home/pi/plantmonitor/api.service /etc/systemd/system/;
  sudo cp /home/pi/plantmonitor/robot.service /etc/systemd/system/;
  sudo cp /home/pi/plantmonitor/gardener.service /etc/systemd/system/;

  sudo systemctl enable api.service;
  sudo systemctl enable robot.service;
  sudo systemctl enable gardener.service;
  sudo systemctl start api.service;
  sudo systemctl start robot.service;
  sudo systemctl start gardener.service;
  "

reboot_robots="
    sudo reboot;"
#sudo systemctl start robot.service;
pssh -i -h robot_list0.txt -P -t 10000000 $update_command
