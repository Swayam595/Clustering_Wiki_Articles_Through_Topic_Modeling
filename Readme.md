### For internal reference
Add all links/implementation details/shared resources here.

### Preprocessing
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

### Evaluation (Graph Analysis)
[Power Iteration Clustering](https://spark.apache.org/docs/latest/mllib-clustering.html#power-iteration-clustering-pic)
- PIC is a graph clustering algorithm which uses **Affinity matrix** as input and returns clusters based on their similarities.
- Affinity matrix is such that it **`A(ij) = sim(i,j)`**. Where i and j are any two nodes and sim is the similarity between them.
- Graph with simialrities between each pair of nodes as weights on the edge is used for clustering the Graph using PIC.
