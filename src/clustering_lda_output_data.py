
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

data_folder = base_folder + "/results/lda_results/"

lda_output_path = data_folder + "lda_model_results.csv"
wiki_data_path = data_folder + "articles_title.txt"

wiki_data = pd.read_csv(wiki_data_path, index_col=None, names = ["page_id", "title"])


sc = SparkContext()
sqlContext = SQLContext(sc)


lda_data = sqlContext.read.csv('file://' + lda_output_path, header=True, inferSchema= True, encoding="utf-8")


vectorAssembler = VectorAssembler(inputCols=lda_data.columns, outputCol="features")
data_to_cluster = vectorAssembler.transform(lda_data)


results = []



kmeans_100 = KMeans().setK(100).setSeed(999)

model_100 = kmeans_100.fit(data_to_cluster.select('features'))
model_100.save(data_folder + "k_means_model_100_results")

result = model_100.transform(data_to_cluster)
results.append([100, result])



kmeans_50 = KMeans().setK(50).setSeed(999)

model_50 = kmeans_50.fit(data_to_cluster.select('features'))
model_50.save(data_folder + "k_means_model_50_results")

result = model_50.transform(data_to_cluster)
results.append([50, result])



kmeans_35 = KMeans().setK(35).setSeed(999)

model_35 = kmeans_35.fit(data_to_cluster.select('features'))
model_35.save(data_folder + "k_means_model_35_results")

result = model_35.transform(data_to_cluster)
results.append([35, result])


evaluator = ClusteringEvaluator()

for preds in results:
    k = preds[0]
    predictions = preds[1]

    silhouette = evaluator.evaluate(predictions)

    predictions_df = prediction.select("prediction").toPandas()
    predictions_df.index = wiki_data.page_id.tolist()[:len(predictions_df)]
    predictions_df.to_csv(data_folder + "k_means_lda_clustering" + str(k) +  ".csv")

    predictions.select("features", "prediction").toPandas().to_csv(data_folder + "k_means_data" + str(k) +  ".csv")

