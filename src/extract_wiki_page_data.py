# This script creates an adjacency list and an adjacency matrix from raw wikidump SQL scripts
# Author: Aashay Mokadam


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

# Initialization of variables and spark contexts

base_folder = os.path.abspath("..")
raw_data_folder = os.path.join(base_folder, "data/")
preprocessed_data_folder = os.path.join(base_folder, "preprocessed/")

adj_graph_data = os.path.join(preprocessed_data_folder, 'adjacency_graph_data/')
adj_lists = os.path.join(preprocessed_data_folder, 'adjacency_lists/')

page_file_name = "enwiki-20191101-page.sql"
page_file = os.path.join(raw_data_folder, page_file_name)
page_file_columns = ["page_id", "page_namespace", "page_title", "page_restrictions", 
                     "page_is_redirect", "page_is_new", "page_random", "page_touched", 
                     "page_links_updated", "page_latest", "page_len", "page_content_model", 
                     "page_lang"]

page_link_file_name = "enwiki-20191101-pagelinks.sql"
page_link_file = os.path.join(raw_data_folder, page_link_file_name)
page_link_file_columns = ["pl_from", "pl_namespace", "pl_title", "pl_from_namespace"]

sc = SparkContext()
sqlContext = SQLContext(sc)

# Functions:

def GetPageDatabaseEntries(line):

    data = []

    line = re.sub("INSERT INTO `page` VALUES","",line).strip()
    line = re.sub(";","",line).strip()
    line = re.sub(r"NULL\)",r"'NULL')",line).strip()
    line = re.sub(r",NULL,",r",'NULL',",line).strip()
    line = re.sub(r"\),\(", r")\n(", line)

    for t in line.split("\n"):
        try:
            d = list(ast.literal_eval(t))
            data.append(d)
        except:
            pass

    return data

def GetPageLinkDatabaseEntries(line):
    
    data = []

    # (\([^,]+,[^,]+,'[^,]+',[^,]+\))
    # (\([^,]+,[^,]+,'(?:[^'\\]|\\.)+',[^,]+\))
    # regex = r"\([^,]+,[^,]+,'[^,]+',[^,]+\)"
    regex = r"\([^,]+,[^,]+,'(?:[^'\\]|\\.)+',[^,]+\)"

    line = re.sub("INSERT INTO `pagelinks` VALUES","",line).strip()
    line = re.sub(";","",line).strip()
    
    tuples = re.findall(regex, line)

    for t in tuples:
        try:
            d = list(ast.literal_eval(t))
            R = Row("pl_from", "pl_namespace", "pl_title", "pl_from_namespace")
            d_row = R(d[0], d[1], d[2], d[3])
            data.append(d_row)
        except:
            pass 

    return data


def GetToPageIds(row, id_name_map, redirect_map):

    page_ids = row['pl_from'].split(",")
    link_name = row['pl_title']

    to_link_id = 0
        
    try:
        link_id = id_name_map.at[link_name, 'page_id']
        to_link_id = str(link_id)

    except:
        try:
            redirect_name = redirect_map.at[link_name, 'pl_title']
            redirect_name = redirect_name.split(";")[0]

            link_id = id_name_map.at[redirect_name, 'page_id']
            to_link_id = str(link_id)

        except:
            try:
                if "\"" not in link_name:
                    raise Exception

                new_link_name = re.sub("\"", "\"\"", link_name).strip()
                new_link_name = "\"" + new_link_name + "\""
                link_id = id_name_map.at[new_link_name, 'page_id']
                to_link_id = str(link_id)

            except:
                pass

    r = Row('from_page_ids', 'to_page_id')
    return [[r(page_ids, to_link_id)]]


page_data_map_df, page_redirect_links = None, None

# Get Page Data:

###################################################
######### GENERATE DATA FROM SQL SCRIPTS ##########
###################################################
if os.path.exists(os.path.join(preprocessed_data_folder, 'wiki_page_data.csv')) == False or os.path.exists(os.path.join(preprocessed_data_folder, 'wiki_page_data_redirects.csv')) == False:

    pages = sc.textFile('file://' + page_file)

    page_data_vals = pages.filter(lambda x: x.startswith("INSERT INTO"))
    page_data_vals = page_data_vals.map(lambda l: GetPageDatabaseEntries(l)).reduce(lambda a,b: a+b)

    page_data_df = pd.DataFrame(page_data_vals, columns=page_file_columns)
    page_data_df = page_data_df.set_index("page_id")

    page_data_df.head()

    # page_data_df.to_csv(preprocessed_data_folder + 'wiki_page_data_raw.csv')


    page_data_df_less = page_data_df.drop(columns=["page_restrictions", 
                        "page_is_new", "page_random", "page_touched", 
                        "page_links_updated", "page_latest", "page_content_model", 
                        "page_lang"])
    # page_data_df_less.to_csv(preprocessed_data_folder + 'wiki_page_data_all_pagetypes.csv')

    page_data_df_less = page_data_df_less.loc[page_data_df_less["page_namespace"] == 0].drop(columns=["page_namespace"])

    page_data_df_redirects = page_data_df_less.loc[page_data_df_less["page_is_redirect"] == 1].drop(columns=["page_is_redirect"])
    page_data_df_redirects.to_csv(preprocessed_data_folder + 'wiki_page_data_redirects.csv')

    page_data_df_fin = page_data_df_less.loc[page_data_df_less["page_is_redirect"] == 0].drop(columns=["page_is_redirect"])
    page_data_df_fin.to_csv(preprocessed_data_folder + 'wiki_page_data.csv')

    page_data = sqlContext.createDataFrame(page_data_df_fin.reset_index())
    page_data_map_df = page_data_df_fin.set_index("page_title")


###################################################
############# READ FROM FILES INSTEAD #############
###################################################

else:
    page_data = sqlContext.read.csv('file://' + preprocessed_data_folder + 'wiki_page_data.csv', header=True, inferSchema= True, encoding="utf-8")
    page_data_map_df = page_data.toPandas().set_index("page_title")

###################################################
####################### FIN #######################
###################################################

page_id_name_mapping = sc.broadcast(page_data_map_df)

# Get Page Link Data:
page_links = sc.textFile('file://' + page_link_file)

page_link_data = page_links.filter(lambda x: x.startswith("INSERT INTO"))
page_link_data = page_link_data.map(lambda l: GetPageLinkDatabaseEntries(l))

page_link_data_df = page_link_data.flatMap(lambda x: x).toDF()

page_link_data_df = page_link_data_df.filter((page_link_data_df.pl_namespace == 0) & (page_link_data_df.pl_from_namespace == 0))
page_link_data_df = page_link_data_df.drop('pl_namespace', 'pl_from_namespace')

# Create and store page redirect link map

####################################################
################# CREATE REDIR MAP #################
####################################################

if os.path.exists(os.path.join(preprocessed_data_folder, 'wiki_page_data_link_redirects.csv')) == False:
    
    page_data_df_redirects = sqlContext.read.csv('file://' + preprocessed_data_folder + 'wiki_page_data_redirects.csv', header=True, inferSchema= True, encoding="utf-8")
    page_data_df_redirects = page_data_df_redirects.toPandas()

    page_redirect_df = sqlContext.createDataFrame(page_data_df_redirects.reset_index())
    page_redirect_links = page_link_data_df.join(page_redirect_df, page_link_data_df.pl_from == page_redirect_df.page_id).toPandas()
    page_redirect_links.to_csv(preprocessed_data_folder + 'wiki_page_data_link_redirects.csv')
    page_redirect_links = page_redirect_links.set_index("page_title")


####################################################
############# READ FROM FILES INSTEAD ##############
####################################################

else:
    page_redirect_links = sqlContext.read.csv('file://' + preprocessed_data_folder + 'wiki_page_data_link_redirects.csv', header=True, inferSchema= True, encoding="utf-8")
    page_redirect_links = page_redirect_links.toPandas().set_index("page_title")

####################################################
####################### FIN ########################
####################################################

page_redirect_mapping =  sc.broadcast(page_redirect_links)

# Remove from_links that are redirects
page_link_data_df = page_link_data_df.join(page_data, page_link_data_df.pl_from == page_data.page_id, how="inner")
page_link_data_df = page_link_data_df.drop('index', 'page_id', 'page_title', 'page_len')

# Get all page_ids that go into a link
from_page_ids_data_df = page_link_data_df.groupBy(["pl_title"]).agg(collect_list("pl_from").alias("pl_from")).withColumn("pl_from", concat_ws(",", col("pl_from")))

# Create Graph Data

# Map to-link from titles to page_ids
from_page_ids_data_df = from_page_ids_data_df.rdd.flatMap(lambda row: GetToPageIds(row, page_id_name_mapping.value, page_redirect_mapping.value)).flatMap(lambda x: x).toDF()
from_page_ids_data_df = from_page_ids_data_df.filter("to_page_id IS NOT NULL AND to_page_id != 0")
# Convert to 1:1 to-link:from-link 
from_page_ids_data_df = from_page_ids_data_df.select(explode(from_page_ids_data_df.from_page_ids).alias("from_page_id"), from_page_ids_data_df.to_page_id)

from_page_ids_data_df = from_page_ids_data_df.withColumn("from_page_id", from_page_ids_data_df["from_page_id"].cast(IntegerType()))
from_page_ids_data_df = from_page_ids_data_df.withColumn("to_page_id", from_page_ids_data_df["to_page_id"].cast(IntegerType()))

# Save Graph Data

print("Data: " )
from_page_ids_data_df.printSchema()
from_page_ids_data_df.coalesce(4).write.csv(adj_graph_data, header = 'true')

#from_page_ids_data_pd_df = from_page_ids_data_df.toPandas()
#from_page_ids_data_pd_df.to_csv(preprocessed_data_folder + 'adjacency_graph_data.csv')


# Create Adjacency List
create_adj_list = False

if create_adj_list == True:
    print("Adjacency List: ")
    adjacency_list_df = from_page_ids_data_df.groupBy(["from_page_id"]).agg(collect_list("to_page_id").alias("to_page_id")) 
    adjacency_list_df.coalesce(4).write.csv(adj_lists, header = 'true')
    
#    adjacency_list_df = adjacency_list_df.toPandas()
#    adjacency_list_df.to_csv(preprocessed_data_folder + 'adjacency_list.csv')


# Create Adjacency Matrix
create_adj_matrix = False

if create_adj_matrix == True:
    
    print("Adjacency Matrix: ")
    adjacency_matrix_df = pd.crosstab(from_page_ids_data_pd_df.from_page_id, from_page_ids_data_pd_df.to_page_id)
    idx = adjacency_matrix_df.columns.union(adjacency_matrix_df.index)
    adjacency_matrix_df = adjacency_matrix_df.reindex(index = idx, columns=idx, fill_value=0)


    try:
        zero_cols = adjacency_matrix_df.loc[:, (adjacency_matrix_df == 0).all(axis=0)].columns.values.tolist()
        zero_rows = adjacency_matrix_df.loc[(adjacency_matrix_df == 0).all(axis=1)].index.values.tolist()
        to_drop = list(set(zero_cols).intersection(zero_rows))

        print("Dropping {} rows and columns".format(str(len(to_drop))))

        adjacency_matrix_df = adjacency_matrix_df.drop(to_drop, axis=1)
        adjacency_matrix_df.to_csv(preprocessed_data_folder + 'adjacency_matrix_reduced.csv')

    except:
        print("Dropping rows and columns failed!")
        pass

    adjacency_matrix_df.head(20)
    adjacency_matrix_df.to_csv(preprocessed_data_folder + 'adjacency_matrix.csv')

print("Done")
