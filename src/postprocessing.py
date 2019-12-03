import numpy as np
import pandas as pd
import os


base_folder = os.path.abspath("..")
preprocessed_data_folder = os.path.join(base_folder, "preprocessed/")

input_file = preprocessed_data_folder + 'adjacency_graph_data.csv'
output_graph = preprocessed_data_folder + 'adjacency_graph_final_data.csv'
output_wiki = preprocessed_data_folder + 'indexed_wiki_data.csv'

# Read Data

graph_df = pd.read_csv(input_file, sep=",", index_col=None, names = ["from_page_id", "to_page_id"])
graph_df["sims"] = 1

wiki_data = pd.read_csv(preprocessed_data_folder + "wiki-data/articles_title.txt", index_col=None, names = ["page_id", "title"])


# Merge on available Page IDs

right = wiki_data
ids = wiki_data["page_id"].tolist()

final = graph_df[graph_df['from_page_id'].isin(ids) & graph_df['to_page_id'].isin(ids)]

# Write Data

final.to_csv(output_graph, index=False)

wiki_data.index = wiki_data.index + 1
wiki_data.to_csv(output_wiki, index=True)
