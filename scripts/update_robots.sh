#!/bin/bash

update_command="
  sudo systemctl disable robot;
  sudo systemctl stop robot;

  cd /home/pi/robot_testing/The_*/logs;

  echo 'Archiving Finished! Updating...';

  cd /home/pi/robot_testing/;
  git pull;

  echo 'Finished pulling from git';

  sudo rm /etc/systemd/system/serial.service;
  sudo cp /home/pi/plantMonitor/robot.service /etc/systemd/system/;

  sudo systemctl enable robot;
  sudo systemctl start robot;
  "

reboot_robots="
    sudo reboot;"

pssh -i -h robot_list0.txt -P -t 10000000 $update_command
