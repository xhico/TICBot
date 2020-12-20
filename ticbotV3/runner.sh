#!/bin/sh

clear

rm -rf archive/*
rm -rf feeds/*

for value in TIC EINF CMU EME ECN GES LRE PSI
do
   echo 2018-10-02 11:08:32 > archive/$value.txt
done

#python eder.py