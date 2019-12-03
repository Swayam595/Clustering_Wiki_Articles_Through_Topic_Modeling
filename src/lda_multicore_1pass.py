import logging
import gensim
import pandas as pd
import argparse
import time
from gensim.models.ldamulticore import LdaMulticore
from gensim.test.utils import datapath

start_time = time.time()

print ("\n\n<----------- Entering LDA modeling script ----------->\n\n")
parser = argparse.ArgumentParser(description='Requires two inputs, path to wiki dump and path to the directory to write the output ')
parser.add_argument("-i" , help="Path to input tf-idf, wordids and article title file")
parser.add_argument("-o" , help="Path to the directory to write the output")

args = parser.parse_args()
input_file_path = args.i
output_path = args.o


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

id2word = gensim.corpora.Dictionary.load_from_text(input_file_path + '/wiki_en_wordids.txt')

mm = gensim.corpora.MmCorpus(input_file_path + '/wiki_en_tfidf.mm')

print (mm)

print ("\n\n<----------- Starting LDA modeling ----------->\n\n")

lda = LdaMulticore(corpus=mm, id2word=id2word, num_topics=100, passes=1)

print ("\n\n<----------- LDA modeling finished. Now saving the model to disk ----------->\n\n")


print ("\n\n<----------- Saving Model Complete ----------->\n\n")


try:
    path = output_path +'/model_1pass'
    lda.save(path)
except:
    print ("\n\n<----------- Saving LDA Model failed ----------->\n\n")


print ("\n\n<----------- Writing Article and their topic weight to pandas ----------->\n\n")
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

print("\n\n--- Writing pandas took in %s seconds ---" % (time.time() - pandas_write_time))
print ("\n\n<----------- Writing Article and their topic weight to pandas finished ----------->\n\n")

result.to_csv(output_path + "/articles_topics_5pass_1.csv", index=False)

print("\n\n--- Total time took in %s seconds ---" % (time.time() - start_time))
print ("\n\n<----------- Exiting LDA modeling script ----------->\n\n")
