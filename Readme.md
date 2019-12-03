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
    +-- slurm*.sh   
+-- preprocessed
|   +-- file_concat-graph.sh
|   +-- all preprocessed files will be stored here
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

### Evaluation (Graph Analysis)
[Power Iteration Clustering](https://spark.apache.org/docs/latest/mllib-clustering.html#power-iteration-clustering-pic)
- PIC is a graph clustering algorithm which uses **Affinity matrix** as input and returns clusters based on their similarities.
- Affinity matrix is such that it **`A(ij) = sim(i,j)`**. Where i and j are any two nodes and sim is the similarity between them.
- Graph with simialrities between each pair of nodes as weights on the edge is used for clustering the Graph using PIC.
