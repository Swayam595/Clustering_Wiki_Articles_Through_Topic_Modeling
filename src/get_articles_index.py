from gensim.test.utils import datapath, get_tmpfile
from gensim.corpora import WikiCorpus, MmCorpus
import pickle
import argparse

print ("Retriving wiki article and their IDs")

parser = argparse.ArgumentParser(description='Requires two inputs, path to wiki dump and path to the directory to write the output ')
parser.add_argument("-i" , help="Path to input wiki dump")
parser.add_argument("-o" , help="Path to the directory to write the output")
args = parser.parse_args()
input_file = args.i
output_path = args.o

path_to_wiki_dump = datapath(input_file)

print ("Creating wiki corpous")
wiki = WikiCorpus(path_to_wiki_dump)

output_fname = get_tmpfile(output_path+"/wiki_en.mm")

print ("Serializing the wiki corpous")
MmCorpus.serialize(output_fname, wiki, metadata = True)

with open(output_path+"/wiki_en.mm.metadata.cpickle", 'rb') as meta_file:
    docno2metadata = pickle.load(meta_file)

j = 1

print ("Writing the articles and their IDs into a text file")
with open(output_path+'/articles_title.txt', 'w') as fp:
    for i in docno2metadata:
        if j%10000 == 0:
            print ('%s articles and their IDs are fetched'%(j))
        fp.write('%s, %s \n'%(docno2metadata[i][0],docno2metadata[i][1]))

        j += 1

print ("Retrival of wiki article and IDs finished")
