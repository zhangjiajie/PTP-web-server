#!/bin/bash
#PBS -q batch
#PBS -l nodes=1:ppn=1
#PBS -V 
#PBS -o localhost:/home/jiajie/ptpo.txt
#PBS -e localhost:/home/jiajia/ptpe.txt 

python3 /home/jiajie/Personal/PTP/bin/bPTP.py -t /home/jiajie/Personal/PTP/example/ptp_example.tre -o /home/jiajie/ptpres -s 1234

