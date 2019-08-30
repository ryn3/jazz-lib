

# dir="data"
# for f in "$dir"/*; do
# 	python xml2json.py -t xml2json -o $f".json" "$f"
# 	mv $f".json" JSON_final_masters
# done

dir="JSON_final_masters"
for f in "$dir"/*; do
	mongoimport -d final_jazz_releases -c temp "$f"
done


mongo < aggregate_masters.js

echo "Done with importing to Mongo."
