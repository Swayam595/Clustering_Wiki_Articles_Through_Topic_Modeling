# Clustering Wikipedia articles using LDA topic modeling and graph analysis

## Data 

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

## Directory Structure
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
|   +-- all preprocessed files will be written here
+-- results
|   +-- lda_results
|       +-- lda_model_results.csv (the document-topic file)
|       +-- lda model data
|   +-- file_concat-results.sh
|   +-- clusters_*\
```
## Instructions

#### Text Analysis
**STEP-1 (setup and preprocess of LDA)**
> - Download the latest wikipedia article file from https://dumps.wikimedia.org/enwiki/.
> - Run gensim make_wiki on the downloaded file
> - Python -m gensim.scripts.make_wiki ~/path_ to_downloaded_wiki_dump ~/path_to_the_directrory_save_output.
> - Running this will create the word id text file and tf-idf mm file.
> - The program doesn’t create the meatdata.cpickle file in HPC so we will create the manually in the next step.

**STEP-2 (Preprocess for LDA)**
> - Run get_wiki_index.sh which takes two inputs one path to the wiki dump and the other is the path of directory where we want to save      the outputs.
> - sbatch get_wiki_index.sh ~/path_ to_downloaded_wiki_dump ~/path_to_the_directrory_save output  
> - After running the following gensim command we will get,
> - wiki_en_wordids.txt.bz2 - Needs to be decompressed manually.
> - articles_title.txt - Contains the article name and its index value
> - wiki_en_tfidf.mm 
> - Creating the all the above files took around 4 hours 50 mins.

**STEP-3 (LDA model and save the document-topic matrix)**
> - Run lda_modeling_1pass.sh or lda_modeling_3pass.sh to create the LDA models and generate a csv having documents as index and             columns as topics. 
> - Both the script takes two inputs.
> - sbatch lda_modeling_1pass.sh ~/path_to_tfidfs_directory ~/path_to_the_directrory_save output 
> - sbatch lda_modeling_3pass.sh ~/path_to_tfidfs_directory ~/path_to_the_directrory_save output 
> - Running both the script will take around +4 hours and +11 hours respectively.
> - Both the scripts will save a trained lda model for future implementation in the directory.

> **IMPORTANT:** Make sure you are following same directory structure as our repo.
> - You may clone our repo to get the directory structure, but make sure the files are placed in appropriate directories as mentioned.
#### Preprocessing script instructions
- Download the enwiki-articles XML file from the link above and store it in **`data/`** directory.
- Command for subset of sql file to consider for graphs.
   ```
  head -n 50 enwiki-20191101-pagelinks.sql > enwiki-20191101-pagelinks-50.sql
  ``` 
  > **NOTE:** replace `-50` with the number of lines of   sql the subset should contain.
- Download both sql files and store them in the **`data/`** directory.
- Run the **`extract_wiki_page_data.py`** script using sbatch command mentioned below.
```
sbatch slurm-spark-submit.sh --conf "spark.driver.memory=100g" --conf "spark.driver.maxResultSize=100g" --conf "spark.network.timeout=10000001" --conf "spark.executor.heartbeatInterval=10000000" extract_wiki_page_data.py
```
> Note: spark.executor.instances = 11(executors per node)*num_nodes - 1 (master)

- The above script will take ~**1-Day** to run based on the configuration of the job.
- This script may generate multiple csv files, based on the write method chosen (write from Pandas vs write from PySpark Dataframes).     These files can be concatenated using **`python3 shell_caller.py preprocessed`**. The concatenated file will be stored in               **`preprocessed/`** directory as **`adjacency_graph_data.csv`**.
- Run the **`postprocessing.py`** script to get the **`adjacency_graph_final_data.csv`**, which will be used in the steps that follow.     This script ensures that the surviving nodes are those with LDA data available.
#### Speed up preprocessing step
- You can download these 3 csv files to speed up the preprocessing step.
- Download all the folders from this link and store them in `preprocessed/` folder.
- [Drive link to files](https://drive.google.com/open?id=1LvizePKdElHm9z6hddXK_GaXzqZLI9lj)
- The preprocessing script will automatically read from these files and skip the steps that creates these files.

#### PIC clustering instructions
- Run this script through the postprocessing script to get the final csv that is ready to be trained using PIC clustering. Make sure a     file named **`adjacency_graph_final_data.csv`** is generated in the **`preprocessed/`** directory.
- Now run the pic_clustering.py script to cluster the graph. This script will generate the clusters csv file and save them to the         directory **`clusters_(number of iterations)/`** directory in multiple csv files.
- Now run the same **`python3 shell_caller.py results`** to concatenate all the csvs in different clusters directories. The final csvs     generated will follow this naming convention **`final_100-(num_iterations).csv`** ~**4.7 million lines**.
- To check progress of the pic_clustering job you may use **`grep -n "model trained" job_name.log`** -> prints for which num_iterations   the job finished. The time taken by this job is ~**less than 10 hrs**, based on the configuration used. 
- You have the pic_clusters file ready.

## Evaluation
- Evaluation of cluster cohesion using **`silhouette score`**.[[ref]](https://en.wikipedia.org/wiki/Silhouette_(clustering))
- Silhouette score on LDA clustering: **`0.61 (K = 50 clusters)`**
- Silhouette score range: -1 to 1 with 1 being the best score.
