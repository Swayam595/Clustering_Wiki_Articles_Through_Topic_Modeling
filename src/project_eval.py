#!/usr/bin/env python
# coding: utf-8
# author: map Karthik



import sys
from pyspark import SparkConf, SparkContext
from pyspark.mllib.clustering import PowerIterationClustering, PowerIterationClusteringModel
conf = SparkConf()
sc = SparkContext.getOrCreate(conf=conf)

data = sc.textFile(sys.argv[1])
sims = data.map(lambda line: tuple([float(x) for x in line.split(' ')]))

#sims.collect()


model = PowerIterationClustering.train(sims,5,10)

print(model.assignments().collect())





