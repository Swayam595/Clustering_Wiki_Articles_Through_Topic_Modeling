#!/bin/bash

#SBATCH --nodes=1
#SBATCH --mem-per-cpu=8G
#SBATCH --cpus-per-task=5
#SBATCH --ntasks-per-node=10
#SBATCH --job-name=lda_multicore
#SBATCH --time=1-00:00:00

export Input_File=$1
export Output_Directory=$2

module load python3

python /home/013725595/CMPE_256/temp1/temp.py -i $Input_File -o $Output_Directory
