#!/usr/bin/env python
# coding: utf-8
# author: map Karthik



import sys
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.mllib.clustering import PowerIterationClustering, PowerIterationClusteringModel
import os
conf = SparkConf()
sc = SparkContext.getOrCreate(conf=conf)
sqlCon = SQLContext(sc)

base_folder = os.path.abspath("..")
raw_folder = os.path.join(base_folder,"data/")
dat_folder = os.path.join(base_folder,"src/")
preprocessed_folder = os.path.join(base_folder,"preprocessed/")

data = sc.textFile(dat_folder+'sim_pic_data.csv')
header = data.first()

def initialProcess(lines):
    x= lines.split(',')
    x = (int(x[0]),int(x[1]),float(x[2]))
    return x

sims=data.filter(lambda x:  x!=header).map(initialProcess)

#sims.collect()


model = PowerIterationClustering.train(sims,5,10)

#Saving Clusters
clusters = model.assignments()
clustRDD = clusters.map(lambda x: (x.id,x.cluster))
clust_df = clustRDD.toDF().toPandas()

#clust_df.coalesce(2).write.csv('clusters',header = 'true')

clust_df = clust_df.rename(columns={'_1':'NodeID','_2':'Cluster'})
clust_df.to_csv('clusters.csv',index=False)






