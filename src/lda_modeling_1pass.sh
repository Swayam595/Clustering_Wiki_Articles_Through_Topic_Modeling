#!/bin/bash

#SBATCH --nodes=1
#SBATCH --cpus-per-task=5
#SBATCH --ntasks-per-node=10
#SBATCH --mem-per-cpu=8G
#SBATCH --job-name=lda_3pass
#SBATCH --partition=gpu
#SBATCH --gres=gpu
#SBATCH --time=24:00:00

export Input_File=$1
export Output_Directory=$2

module load python3

python /home/013725595/CMPE_256/Project/src/python_scripts/lda_modeling_1pass.py -i $Input_File -o $Output_Directory
