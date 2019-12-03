
import ast
import re
import numpy as np
import pandas as pd
import os

import pyspark
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import *

base_folder = os.path.abspath("..")
preprocessed_data_folder = os.path.join(base_folder, "preprocessed/")
input_file = preprocessed_data_folder + 'adjacency_graph_data.csv'
output_graph = preprocessed_data_folder + 'adjacency_graph_data_final.csv'
output_pic = preprocessed_data_folder + 'adjacency_graph_data_pic.csv'

# sc = SparkContext()
# sqlContext = SQLContext(sc)
# graph_data = sc.textFile('file://' + input_file)

graph_df = pd.read_csv(input_file, sep=";", index_col=None)
