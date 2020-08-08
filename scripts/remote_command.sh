#!/bin/bash
#cygwin TODO: make second argument into selecting one of the robot list files
#DATE=`date '+%Y-%m-%d %H:%M:%S.000' --date='+20 seconds'`
#osx
TEST_DATE=$(date -v+40S '+%Y-%m-%d %H:%M:%S.000' | tr -d '\n')
TEXT=$TEST_DATE,$1
  echo $TEXT
if ([[ $1 =~ ^[DUTLNFX]{1}$ ]] && [[ $2 =~ ^[01234A]{1}$ ]] ); then
  if  [[ "$2" = "A" ]]; then
  #using a for loop cause too much delay issues
    cat "robot_list1.txt" >> all.txt
    cat "robot_list2.txt" >> all.txt
    cat "robot_list3.txt" >> all.txt
    cat "robot_list4.txt" >> all.txt
    TEST_DATE=$(date -v+40S '+%Y-%m-%d %H:%M:%S.000' | tr -d '\n')
    TEXT=$TEST_DATE,$1
    ROBOTLIST="all.txt"
    pssh -i -t 40 -h  $ROBOTLIST "echo $TEXT >> ~/robot_testing/The_Wireless_Army/logs/scheduled_actions.csv"
    rm all.txt
  else
    ROBOTLIST="robot_list$2.txt"
    pssh -i -t 25 -h $ROBOTLIST "echo $TEXT >> ~/robot_testing/The_Wireless_Army/logs/scheduled_actions.csv"
  fi
else
  echo "INVALID INPUT"
  echo "First Argument N / T / U / L / D / F / X"
  echo "Second Argument 0 / A / 1 / 2 / 3 / 4 "
  echo "which stand for Test/ all / shelf 1 / shelf 2 / shelf 3 / shelf 4 "
  exit 1
fi
