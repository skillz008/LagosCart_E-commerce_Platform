# Portfolio 4 — NoSQL and advanced data models (7 marks)

## Implemented model
An educational document-oriented catalogue is implemented by document_store.py using Python dictionaries persisted as a JSON object keyed by product _id. It is a custom file-based NoSQL store, NOT MongoDB and not SQL JSON columns. The root runner executes insert, category filtering, nested-attribute update, reload, duplicate rejection and delete. Evidence: document-tests.json and catalogue-example.json.

Phone attributes (RAM/storage/network) differ from shirt attributes (size/fabric). Embed bounded variant lists because they are read with the product. Keep customer orders/payment records relational; a mutable price in the catalogue must not rewrite sale-time prices. Catalogue document IDs map conceptually to relational SKUs; the small document fixture is an independent demonstration, not an automatically synchronised export of relational product facts.

## Trade-offs
Flexible nested attributes avoid numerous mostly-null category-specific columns. Embedding can reduce application joins for a product detail page, but large/unbounded variant arrays are unsuitable; reference independently queried entities. The custom find operation scans documents: no performance advantage is measured or claimed. Cross-document referential integrity, indexes, concurrent transactions, access control and recovery are not implemented.

save writes a temporary file then replaces the destination. This is a single-file replacement technique, not a guarantee of database-grade ACID, filesystem power-failure durability or multi-process safety. Concurrent writers can lose changes. No fsync-based crash guarantee is provided.

## Optional established DBMS
mongodb-optional.js provides a local mongosh upsert/index/query example based on the same model. It was not executed in this environment. It requires a running local MongoDB server and mongosh. Capture your actual output if you use it. If the lecturer requires an established NoSQL DBMS rather than a custom document-store implementation, run and document this extension before submission.

Design reading: MongoDB official Embedded Data Versus References and Reference Data documentation; URLs in documentation/sources.md. Their MongoDB guarantees must not be attributed to this custom store.
