### For internal reference
Add all links/implementation details/shared resources here.

### Preprocessing
#### Instructions
1) Download, extract and place "enwiki-20191101-page.sql" and "enwiki-20191101-pagelinks.sql" in the "data/" folder
2) For a sample subset of pagelinks, navigate to the "data/" folder, run the below command, and switch the source file name in the script:
```
head -n 50 enwiki-20191101-pagelinks.sql > enwiki-20191101-pagelinks-50.sql
```

#### To submit jobs, use the below configuration:
```
sbatch slurm-spark-submit.sh --conf "spark.driver.memory=100g" --conf "spark.driver.maxResultSize=100g" --conf "spark.network.timeout=10000001" --conf "spark.executor.heartbeatInterval=10000000" extract_wiki_page_data.py
```
spark.executor.instances = 11(executors per node)*num_nodes - 1 (master)

#### Reference to original gensim script for preprocessing:
python -m gensim.scripts.segment_wiki -f enwiki-20171001-pages-articles.xml.bz2 -o wiki-en.gz

#### Link to "List of all page titles":
https://dumps.wikimedia.org/enwiki/20191101/enwiki-20191101-all-titles.gz

#### Link to "Base per-page data (id, title, old restrictions, etc)":
https://dumps.wikimedia.org/enwiki/20191101/enwiki-20191101-page.sql.gz

#### Link to "Articles, templates, media/file descriptions, and primary meta-pages":
https://dumps.wikimedia.org/enwiki/20191101/enwiki-20191101-pages-articles.xml.bz2
##### Sample:
https://dumps.wikimedia.org/enwiki/20191101/enwiki-20191101-pages-articles14.xml-p7697599p7744799.bz2

#### Link to "Wiki page-to-page link records":
https://dumps.wikimedia.org/enwiki/20191101/enwiki-20191101-pagelinks.sql.gz

### Text Analysis

### Directory Structure
```
.
+-- data
|   +-- *.sql
|   +-- *xml.bz
+-- src
|   +-- extract_wiki_page_data.py
|   +-- pic_clustering.py
|   +-- slurm*.sh   
|   +-- lda_modeling_1pass.py
|   +-- lda_modeling_1pass.sh
|   +-- lda_modeling_3pass.py
|   +-- lda_modeling_3pass.sh
+-- preprocessed
|   +-- file_concat-graph.sh
|   +-- all preprocessed files will be stored here
|   +-- wiki_en_wordids.txt
|   +-- wiki_en.tfidf_model
|   +-- articles_title.txt
+-- results
|   +-- file_concat-results.sh
|   +-- clusters_*\
```
### Instructions
- Download the enwiki-articles XML file from the link above and store it in `data/` directory.
- Download both sql files and store them in the `data/` directory.
- run the extract_wiki_page_data.py script using sbatch command mentioned above.
- The above script will take ~**1-Day** to run based on the configuration of the job.
- Make sure you are following same directory structure as our repo.

### LDA Modeling Instructions
- Download the latest wikipedia article file from https://dumps.wikimedia.org/enwiki/.
- Run gensim make_wiki on the downloaded file
  - Python -m gensim.scripts.make_wiki ~/path_ to_downloaded_wiki_dump ~/path_to_the_directrory_save_output
    - Running this will create the word id text file and tf-idf mm file.
    - The program doesn’t create the meatdata.cpickle file in HPC so we will create the manually in the next step.
  - Run get_wiki_index.sh which takes two inputs one path to the wiki dump and the other is the path of directory where we want to save the outputs.
    - sbatch get_wiki_index.sh ~/path_ to_downloaded_wiki_dump ~/path_to_the_directrory_save output  
  - After running the following gensim command we will get,
    - wiki_en_wordids.txt.bz2 - Needs to be decompressed manually.
    - articles_title.txt - Contains the article name and its index value
    - wiki_en_tfidf.mm
  - Creating the all the above files took around 4 hours 50 mins.
- Run lda_modeling_1pass.sh or lda_modeling_3pass.sh to create the LDA models and generate a csv having documents as index and columns as topics.
  - Both the script takes two inputs.
    - sbatch lda_modeling_1pass.sh ~/path_to_tfidfs_directory ~/path_to_the_directrory_save output
    - sbatch lda_modeling_3pass.sh ~/path_to_tfidfs_directory ~/path_to_the_directrory_save output
  - Running both the script will take around +4 hours and +11 hours respectively.
  - Both the scripts will save a trained lda model for future implementation in the directory.

### Evaluation (Graph Analysis)
[Power Iteration Clustering](https://spark.apache.org/docs/latest/mllib-clustering.html#power-iteration-clustering-pic)
- PIC is a graph clustering algorithm which uses **Affinity matrix** as input and returns clusters based on their similarities.
- Affinity matrix is such that it **`A(ij) = sim(i,j)`**. Where i and j are any two nodes and sim is the similarity between them.
- Graph with simialrities between each pair of nodes as weights on the edge is used for clustering the Graph using PIC.
