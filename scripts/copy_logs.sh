#!/usr/bin/env bash
#for server in pi@172.16.0.131 pi@172.16.0.132 pi@172.16.0.133 pi@172.16.0.134 pi@172.16.0.135 pi@172.16.0.136 pi@172.16.0.137 pi@172.16.0.138 pi@172.16.0.139 pi@172.16.0.140 pi@172.16.0.141 pi@172.16.0.142 pi@172.16.0.143 pi@172.16.0.144 pi@172.16.0.145 pi@172.16.0.146 pi@172.16.0.147 pi@172.16.0.148 pi@172.16.0.149 pi@172.16.0.150 pi@172.16.0.151 pi@172.16.0.152 pi@172.16.0.153 pi@172.16.0.154 pi@172.16.0.155 pi@172.16.0.156 pi@172.16.0.157 pi@172.16.0.158 pi@172.16.0.159 pi@172.16.0.160; do
#    scp -o ConnectTimeout=5 $server:/home/pi/robot_testing/The*/logs/preparse* ~/Desktop/robot_logs7.11/"$server"_file.csv
#    scp -o ConnectTimeout=5 $server:/home/pi/robot_testing/The*/logs/result* ~/Desktop/robot_logs7.11/"$server"_result_file.csv
#done

for server in pi@172.16.0.191 pi@172.16.0.192 pi@172.16.0.193 pi@172.16.0.194 pi@172.16.0.195 pi@172.16.0.196 pi@172.16.0.197 pi@172.16.0.198 pi@172.16.0.199 pi@172.16.0.200; do
    scp -o ConnectTimeout=5 $server:/home/pi/robot_testing/The*/logs/preparse* ~/Desktop/robot_logs7.26/"$server"_file.csv
    scp -o ConnectTimeout=5 $server:/home/pi/robot_testing/The*/logs/result* ~/Desktop/robot_logs7.26/"$server"_result_file.csv
done

#for server in pi@172.16.0.139 pi@172.16.0.142 pi@172.16.0.148 pi@172.16.0.154; do
#    scp -o ConnectTimeout=5 $server:/home/pi/robot_testing/The_*/logs/preparse* ~/Desktop/robot_logs4.15/"$server"_file.csv
#    scp -o ConnectTimeout=5 $3server:/home/pi/robot_testing/The_*/logs/result* ~/Desktop/robot_logs4.15/"$server"_result_file.csv
#done
