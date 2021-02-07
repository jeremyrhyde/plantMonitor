#!/bin/bash

update_command="
  sudo systemctl disable robot.service;
  sudo systemctl disable api.service;
  sudo systemctl stop robot.service;
  sudo systemctl stop api.service;

  echo 'Archiving Finished! Updating...';

  cd /home/pi/plantmonitor/;
  git pull;

  echo 'Finished pulling from git';

  sudo cp /home/pi/plantmonitor/robot.service /etc/systemd/system/;
  sudo cp /home/pi/plantmonitor/api.service /etc/systemd/system/;

  sudo systemctl enable robot.service;
  sudo systemctl enable api.service;
  sudo systemctl start api.service;
  "

reboot_robots="
    sudo reboot;"
#sudo systemctl start robot.service;
pssh -i -h robot_list0.txt -P -t 10000000 $update_command
