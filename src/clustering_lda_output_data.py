import numpy as np
import pandas as pd
import os

os.environ['JAVA_HOME'] = '/scratch/spark/java'

import pyspark
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import *

from pyspark.ml.feature import VectorAssembler

from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

base_folder = os.path.abspath("..")

# configure lda_results_* folder of choice
data_folder = os.path.join(base_folder, "results/lda_results_1_pass/")

lda_output_path = os.path.join(data_folder, "lda_model_results.csv")
wiki_data_path = os.path.join(base_folder, "preprocessed/wiki-data/articles_title.txt")

wiki_data = pd.read_csv(wiki_data_path, index_col=None, names = ["page_id", "title"])


sc = SparkContext()
sqlContext = SQLContext(sc)


lda_data = sqlContext.read.csv('file://' + lda_output_path, header=True, inferSchema= True, encoding="utf-8")

vectorAssembler = VectorAssembler(inputCols=lda_data.columns, outputCol="features")
data_to_cluster = vectorAssembler.transform(lda_data)


results = []


# k = 100


kmeans_100 = KMeans().setK(100).setSeed(999)

model_100 = kmeans_100.fit(data_to_cluster.select('features'))
model_100.save(data_folder + "k_means_model_100")

result = model_100.transform(data_to_cluster)
results.append([100, result])


# k = 50


kmeans_50 = KMeans().setK(50).setSeed(999)

model_50 = kmeans_50.fit(data_to_cluster.select('features'))
model_50.save(data_folder + "k_means_model_50")

result = model_50.transform(data_to_cluster)
results.append([50, result])


# k = 35


kmeans_35 = KMeans().setK(35).setSeed(999)

model_35 = kmeans_35.fit(data_to_cluster.select('features'))
model_35.save(data_folder + "k_means_model_35")

result = model_35.transform(data_to_cluster)
results.append([35, result])


# Evaluating and saving clustering results


evaluator = ClusteringEvaluator()

for preds in results:
    k = preds[0]
    predictions = preds[1]

    silhouette = evaluator.evaluate(predictions)
    
    print("Silhouette Score for k-Means with {} Centers is {}".format(str(k), str(silhouette)))

    predictions_df = predictions.select("prediction").toPandas()
    predictions_df.to_csv(data_folder + "k_means_lda_clustering_" + str(k) +  ".csv")

    predictions.select("features", "prediction").toPandas().to_csv(data_folder + "k_means_data_" + str(k) +  ".csv")


