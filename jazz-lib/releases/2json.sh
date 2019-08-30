dir="done_jazz_data"
for f in "$dir"/*; do
  python xml2json.py -t xml2json -o $f".json" "$f"
  mv $f".json" "$dir"/JSON
done




python xml2json.py -t xml2json -o don_jazz_data/releases_partition_ag.json don_jazz_data/releases_partition_ag