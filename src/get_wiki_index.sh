#!/bin/bash

#SBATCH --nodes=2
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=8
#SBATCH --ntasks-per-node=2
#SBATCH --time=23:10:00
#SBATCH --output=get_wiki_index-srun.log

export Input_File=$1
export Output_Directory=$2

module load python3

python /home/013725595/CMPE_256/Project/src/python_scripts/get_article_index.py -i $Input_File -o $Output_Directory
