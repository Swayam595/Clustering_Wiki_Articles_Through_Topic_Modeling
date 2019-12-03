d=$(pwd)
n=${d: -2}
echo "$n"

cat part*.csv > combined_data.csv
awk 'BEGIN{f=""}{if($0!=f){print $0}if(NR==1){f=$0}}' combined_data.csv > final_100-"$n"_clusters.csv
ls | grep final
