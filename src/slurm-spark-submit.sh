#!/bin/bash
#SBATCH --nodes=8
#SBATCH --cpus-per-task=5
#SBATCH --ntasks-per-node=11
#SBATCH --mem-per-cpu=8G
#SBATCH --job-name=wiki
#SBATCH --output=wiki-srun.log
#SBATCH --partition=gpu
#SBATCH --gres=gpu
#SBATCH --time=2-00:00:00


## --------------------------------------
## 1. Deploy a Spark cluster and submit a job
## --------------------------------------
export SPARK_HOME=/scratch/spark
$SPARK_HOME/deploy-spark-cluster.sh $@

