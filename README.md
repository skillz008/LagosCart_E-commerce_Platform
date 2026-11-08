# LagosCart — MIT 8103 Advanced Database Systems Portfolio

Student: [ENTER YOUR NAME]  
Matriculation number: [ENTER YOUR NUMBER]  
Session: 2026/2027 | Individual practical portfolio | 40 marks  
Private GitHub repository: [INSERT URL AFTER CREATING IT]

## Case study
LagosCart is a simulated Lagos-based online retailer of electronics, fashion and household goods. Customers place orders; catalogue staff maintain products; warehouse staff manage stock; finance staff review payments; delivery staff track fulfilment; managers run sales reports. All data is synthetic, not customer information.

Major records: customers, categories, products, orders, order items, payments and deliveries. Operations: customer order history, catalogue maintenance, checkout, stock reservation, payment recording, fulfilment and reporting. The same business supports all five activities.

## Reproduce
Requires Python 3.10+ with its standard library and SQLite supporting window functions (SQLite 3.25+). No pip packages are needed to run the labs. From the extracted repository root:

```sh
python run_all.py
```

The command rebuilds disposable files in `runtime/` and overwrites generated evidence in the portfolio folders. Do not put personal files in runtime. It creates 100,000 baseline orders and one transaction-test order. It prints a benchmark and exits unsuccessfully if an assertion fails. Benchmark values vary between machines and runs. Reports accompanying this delivery describe the original recorded run; update your reports after rerunning.

Read each portfolio README and `documentation/technical-report.md`. The 3-page PDF is a draft LMS summary. Replace identification and repository placeholders, review the technical reflection, and confirm assessor access before submitting.

## Execution status
- Executed: SQLite schema, synthetic loading, constraints, six query result exports, benchmark, transactions across independent connections, JSON document CRUD/persistence, local application-level replication simulation.
- NOT executed: MongoDB optional script, cloud deployment, networked replication, GitHub publication or LMS submission.
- The custom JSON store is an educational NoSQL document model, not a substitute for MongoDB. Confirm with the lecturer if an established NoSQL DBMS is mandatory.
- The replication lab uses independent local database files; it is not a production distributed cluster. Portfolio 5 permits discussion or setup in the supplied brief.

## Integrity and ownership
This package was prepared with Perplexity assistance and executed in an assistant-managed Python environment. It is a learning and implementation draft, not proof of the student's own progressive work. Run it, inspect it, change it where appropriate, and explain all submitted results. Do not invent prior commits or personal challenges. Keep the AI-use declaration accurate.

## Repository organisation
Each numbered directory contains source and evidence. `runtime/` contains reproducible local databases but is ignored by Git. `documentation/` contains the summary, detailed report, source list and submission checks.

Suggested honest commits, made only when the work occurs: initial case-study scope; schema and constraints; query benchmark; transaction controls; document model; replication exercise; final review. No commit history is supplied.
