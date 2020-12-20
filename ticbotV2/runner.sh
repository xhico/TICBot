#!/bin/sh

clear

cd archive/

array=( one two three )
for i in "${array[@]}"
do
	echo $i
done


#echo 2018-10-02 11:08:32 > TIC.txt


#cd ..
#python ederV2.py