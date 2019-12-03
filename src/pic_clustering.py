#!/usr/bin/env python
# coding: utf-8
# author: map Karthik



import sys
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.mllib.clustering import PowerIterationClustering, PowerIterationClusteringModel
import os
import traceback

# initializing spark
conf = SparkConf()
sc = SparkContext.getOrCreate(conf=conf)
sqlCon = SQLContext(sc)
#directory settings
base_folder = os.path.abspath("..")
raw_folder = os.path.join(base_folder,"data/")
dat_folder = os.path.join(base_folder,"src/")
preprocessed_folder = os.path.join(base_folder,"preprocessed/")
results_folder = os.path.join(base_folder,"results/")

print("Starting to read the file...")
# reading from the graph_sims file
data = sc.textFile(preprocessed_folder+'adjacency_graph_final_data.csv')
header = data.first()

print("File Read...\n")
#mapper to convert data into required form RDD(long,long,double)
def initialProcess(lines):
    x= lines.split(',')
    x = (int(x[0]),int(x[1]),float(x[2]))
    return x

#filtering out the header
sims=data.filter(lambda x:  x!=header).map(initialProcess)

sims.cache()

print("simRDD cached...\n")
num_iterations = [15,20,25] #35,50 take too long 

for num in num_iterations:
    
    try:
        
        # PIC(RDD,num_clusters,num_iterations) defaults: num_iterations=100
        model = PowerIterationClustering.train(sims,100,num)

        print("model trained\t num_iterations:"+str(num)+"\n")
        #Saving Clusters
        clusters = model.assignments()
        clustRDD = clusters.map(lambda x: (x.id,x.cluster))
        clust_df = clustRDD.toDF()

        clust_df.write.csv(results_folder + 'clusters_'+str(num),header = 'true')
        print("csv for {:02d} iterations written".format(num))
    except Exception:
        log = open("exception.log","w+")
        traceback.print_exc(file=log)

print("**************Complete****************")
#clust_df = clust_df.rename(columns={'_1':'NodeID','_2':'Cluster'})
#clust_df.to_csv('clusters.csv',index=False)






