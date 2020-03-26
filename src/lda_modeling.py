import logging
import os
import gensim
import pandas as pd
import argparse
import time
import pathlib

from gensim.models.ldamodel import LdaModel
from gensim.models.ldamulticore import LdaMulticore
from gensim.corpora import Dictionary, MmCorpus
from gensim.test.utils import datapath

start_time = time.time()

print ("\n<----------- ENTERING LDA MODELLING SCRIPT ----------->\n")

parser = argparse.ArgumentParser(description='Generates LDA Models from TF-IDF, WordID, and Article Title files')

parser.add_argument("--input_path", "-i", type=str, help="Path to the directory with tf-idf, wordids, and article title files", required=True)
parser.add_argument("--output_path", "-o", type=str, help="Path to the directory to write the output", required=True)
parser.add_argument("--passes", "-p", type=int, help="Number of passes", default=1)
parser.add_argument("--topics", "-t", type=int, help="Number of topics", default=100)
parser.add_argument("--multicore_model", "-m", action="store_true", help="Whether to use Multicore Mode", default=False)

args = parser.parse_args()
input_directory = args.input_path
output_directory = args.output_path
num_passes = args.passes
num_topics = args.topics
multicore = args.multicore_model

model_name = "lda_results_" + str(num_passes) + "_pass" + "_multicore" if multicore == True else ""
output_path = os.path.join(output_directory, model_name)

pathlib.Path(output_path).mkdir(parents=True, exist_ok=True) 
    
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

id2word = Dictionary.load_from_text(os.path.join(input_directory, 'wiki_en_wordids.txt'))
mm = MmCorpus(os.path.join(input_directory, 'wiki_en_tfidf.mm'))

print ("\n<----------- Starting LDA modeling ----------->\n")
lda_model_time = time.time()

if multicore == False:
    lda = LdaModel(corpus=mm, id2word=id2word, num_topics=num_topics, update_every=1, passes=num_passes)
else:
    lda = LdaMulticore(corpus=mm, id2word=id2word, num_topics=num_topics, passes=num_passes)

print("--- Training the LDA Model took %s seconds ---" % (time.time() - lda_model_time))
print ("\n<----------- LDA modeling finished. Now saving the model to disk ----------->\n")

try:
    path = os.path.join(output_path, 'model')
    lda.save(path)
except:
    print ("\n<----------- Saving LDA Model failed ----------->\n")


print ("\n<----------- Writing Article and their topic weight to pandas ----------->\n")
pandas_write_time = time.time()

temp = dict()
for i in range(len(mm)):
    temp[i] = dict()

index = 0
result = pd.DataFrame()

while index < len (mm):
    vec = mm[index]
    topics = lda.get_document_topics(vec)
    topics = dict(topics)
    temp[index] = topics
    index += 1

result = pd.DataFrame(temp).T
result = result.fillna(0)

print("--- Writing to Pandas DataFrame took %s seconds ---" % (time.time() - pandas_write_time))
print ("\n<----------- Writing Article and Topic Weights to Pandas Finished. Saving to CSV ----------->\n")

result.to_csv(os.path.join(output_path, "lda_model_results.csv"))

print("--- Total time taken was %s seconds ---" % (time.time() - start_time))
print ("\n<----------- LDA MODELLING COMPLETE. EXITING. ----------->\n")
