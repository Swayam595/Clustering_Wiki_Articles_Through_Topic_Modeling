d=$(pwd)
n=${d:37}
echo "$n"

cat adjacency_graph_data/part*.csv > adjacency_graph_data/combined_data.csv
awk 'BEGIN{f=""}{if($0!=f){print $0}if(NR==1){f=$0}}' adjacency_graph_data/combined_data.csv > adjacency_graph_data.csv
ls | grep adjacency_graph_data
