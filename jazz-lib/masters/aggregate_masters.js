db = connect("localhost:27017/final_jazz_releases");

var docs = db.temp.aggregate([{$unwind: {path: "$masters"}}, {$unwind: {path: "$masters.master"}}, {$project: {_id: 0}}])
db.masters.insert(docs.toArray())
db.temp.drop()