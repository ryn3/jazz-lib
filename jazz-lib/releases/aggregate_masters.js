db = connect("localhost:27017/final_jazz_releases");

var docs = db.temp.aggregate([{$unwind: {path: "$releases"}}, {$unwind: {path: "$releases.release"}}, {$project: {_id: 0}}])
db.current.insert(docs.toArray())
db.temp.drop()