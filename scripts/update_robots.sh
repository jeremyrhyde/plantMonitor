#!/bin/bash

update_commands="
sudo systemctl disable robot_new;
sudo systemctl disable screener;
sudo systemctl disable datadog;
sudo systemctl disable api;
sudo systemctl stop robot_new;
sudo systemctl stop screener;
sudo systemctl stop datadog;
sudo systemctl stop api;

cd /home/pi/robot_testing/The_*/logs;
mkdir /home/pi/archive;
mkdir /home/pi/archive/archive;

mv result_* /home/pi/archive/archive;
mv UART_* /home/pi/archive/archive;
mv preparse_* /home/pi/archive/archive;
mv /home/pi/archive/archive /home/pi/archive/archive_$(date '+%Y-%m-%d_%H:%M:%S.000');

rm -f /home/pi/robot_testing/The_Wireless_Army/logs/result_*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/UART_*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/RAW_UART*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/preparse_*;

touch /home/pi/robot_testing/The_Wireless_Army/logs/RAW_UART.log;
touch /home/pi/robot_testing/The_Wireless_Army/logs/result_datadog.log;

echo 'Archiving Finished! Updating...';

echo 'No pull from git';

sudo rm /etc/systemd/system/serial.service;
sudo cp /home/pi/robot_testing/The_Wireless_Army/robot_new.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/screener.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/datadog.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/api.service /etc/systemd/system/;

sudo systemctl enable robot_new;
sudo systemctl enable screener;
sudo systemctl enable datadog;
sudo systemctl enable api;
sudo systemctl start robot_new;
sudo systemctl start screener;
sudo systemctl start datadog;
sudo systemctl start api;"


update_commands_rt2="
sudo systemctl disable robot_new;
sudo systemctl disable screener;
sudo systemctl disable datadog;
sudo systemctl disable api;
sudo systemctl stop robot_new;
sudo systemctl stop screener;
sudo systemctl stop datadog;
sudo systemctl stop api;

cd /home/pi/robot_testing/The_*/logs;
mkdir /home/pi/archive;
mkdir /home/pi/archive/archive;

mv result_* /home/pi/archive/archive;
mv UART_* /home/pi/archive/archive;
mv preparse_* /home/pi/archive/archive;
mv /home/pi/archive/archive /home/pi/archive/archive_$(date '+%Y-%m-%d_%H:%M:%S.000');

rm -f /home/pi/robot_testing/The_Wireless_Army/logs/result_*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/UART_*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/RAW_UART*;
rm -f /home/pi/robot_testing/The_Wireless_Army/logs/preparse_*;

touch /home/pi/robot_testing/The_Wireless_Army/logs/RAW_UART.log;
touch /home/pi/robot_testing/The_Wireless_Army/logs/result_datadog.log;

echo 'Archiving Finished! Updating...';

cd /home/pi/robot_testing/;
git pull;
git reset --hard origin/master_dev;

echo 'Finished pulling from git';

sudo rm /etc/systemd/system/serial.service;
sudo cp /home/pi/robot_testing/The_Wireless_Army/robot_new.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/screener.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/datadog.service /etc/systemd/system/;
sudo cp /home/pi/robot_testing/The_Wireless_Army/api.service /etc/systemd/system/;

sudo systemctl enable robot_new;
sudo systemctl enable screener;
sudo systemctl enable datadog;
sudo systemctl enable api;
sudo systemctl start robot_new;
sudo systemctl start screener;
sudo systemctl start datadog;
sudo systemctl start api;"

cleanup_commands="
  echo 'STOPPING SERVICES';
  sudo systemctl disable robot;
  sudo systemctl disable serial;
  sudo systemctl stop robot;
  sudo systemctl stop serial;
  echo 'GETTING LATEST CODE';
  cd /home/pi/robot_testing/;
  echo 'REMOVING LOGS';
  rm -f /home/pi/robot_testing/The_Wireless_Army/logs/result_*;
  rm -f /home/pi/robot_testing/The_Wireless_Army/logs/UART_*;
  rm -f /home/pi/robot_testing/The_Wireless_Army/logs/RAW_UART*;
  rm -f /home/pi/robot_testing/The_Wireless_Army/logs/preparse_*;

  echo 'STARTING SERVICES';
  sudo cp /home/pi/robot_testing/The_Wireless_Army/robot.service /etc/systemd/system/;
  sudo cp /home/pi/robot_testing/The_Wireless_Army/serial.service /etc/systemd/system/;
  sudo systemctl enable serial;
  sudo systemctl enable robot;
  sudo systemctl start serial;
  sudo systemctl start robot;"

clear_scheduled_commands="
    echo > /home/pi/robot_testing/The_*/logs/scheduled_actions.csv
    sudo reboot;"

reboot_robots="
    sudo reboot;"

add_new_pip3_package="
    echo  'Starting pip install...'
    pip3 install flask_api
    echo  'Installation complete!'
    sudo reboot;"

archive_logs_commands="
    cd /home/pi/robot_testing/The_*/logs;
    mkdir /home/pi/archive;
    mv result_* /home/pi/archive/;
    mv UART_* /home/pi/archive/;
    mv /home/pi/archive/ /home/pi/archive_$(date '+%Y-%m-%d_%H:%M:%S.000');
    echo 'Archiving Finished! Rebooting...';
    sudo reboot;"
#scp -r "../The_Wireless_Army/" pi@192.168.1.22:"/home/pi/robot_testing/"


#<<<<<<< HEAD
#<<<<<<< HEAD
#pssh -i -h robot_list5.txt -P $update_commands
#=======
#<<<<<<< HEAD
#pssh -i -h robot_list0.txt -P $update_commands
#=======
pssh -i -h robot_list0.txt -P -t 10000000 $update_commands_rt2
#pssh -i -h robot_list6.txt -P $cleanup_commands
#>>>>>>> a71763ceb720750f7e4e3baaf4dffae28f7171b7
#>>>>>>> a3a2c877b76695d6c665bd7784b1401650900b61
#=======
#pssh -i -h robot_list3.txt -P $update_commands
#>>>>>>> 63113519e556097041393ad6d75acdbb12b413da
