
mkdir releases/JSON_final_jazz_releases

dir="releases/final_jazz_releases"
for f in "$dir"/*; do
  python3 xml2json.py -t xml2json -o $f".json" "$f"
  mv $f".json" JSON_final_jazz_releases
done

dir="releases/JSON_final_jazz_releases"
for f in "$dir"/*; do
  mongoimport -d final_jazz_releases -c temp "$f"
done

mongo < aggregate_masters.js

echo "Done with importing to Mongo."
