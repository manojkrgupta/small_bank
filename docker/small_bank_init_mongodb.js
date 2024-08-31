db = db.getSiblingDB("small_banks"); // use db

db.createCollection('banks.icici');
db.createCollection('banks.hdfc');

db.banks.icici.ensureIndex({'user': 1}, {unique: true}); // create unique constraint
db.banks.hdfc.ensureIndex({'user': 1}, {unique: true}); // create unique constraint