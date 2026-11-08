// Optional MongoDB implementation. NOT executed in the supplied environment.
// Run against a LOCAL throwaway database: mongosh --file mongodb-optional.js
const lab = db.getSiblingDB('lagoscart_portfolio');
lab.products.updateOne({_id:'SKU-0001'},{$set:{name:'Android Phone',category:'Electronics',price_kobo:12500000,attributes:{ram_gb:8,storage_gb:128},variants:[{colour:'black',sku:'PHONE-BLK'}]}},{upsert:true});
lab.products.createIndex({category:1,'attributes.ram_gb':1});
printjson(lab.products.find({category:'Electronics','attributes.ram_gb':{$gte:8}}).toArray());
