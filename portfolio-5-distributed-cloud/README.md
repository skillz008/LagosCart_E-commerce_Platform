# Portfolio 5 — Distributed and cloud database exercise (6 marks)

## Executed local application-level replication simulation
The runner creates primary.db and replica.db as independent local SQLite files. Primary commits catalogue stock plus a durable outbox event in the same transaction. An explicit deliver() function replays events in sequence. Replica atomically applies an upsert and records the event sequence in applied; repeated delivery checks that marker and skips duplicate events.

Trace in replication-tests.json:
- Publish stock=10 and deliver: both copies 10.
- Pause delivery and commit stock=9 at primary: primary=9, replica=10 (stale read).
- Resume delivery: replica converges to 9.
- Deliver again: exactly two events remain applied (idempotent replay).
- Publish stock=8 without delivering, then close the primary connection to simulate primary unavailability to this client. Replica remains readable at 9.

Closing a connection is an availability simulation, NOT a physical server crash. The file still exists and event 3 remains recoverable. Reading 9 shows exposure to an unreplicated tail if a replica were promoted and the original primary permanently lost; it does not show actual irreversible data loss. No promotion is performed.

## Architecture and consistency discussion
Proposed deployment: web/API service -> relational primary for checkout; asynchronous replica for reporting; separate document catalogue service. Reads requiring current inventory go to primary rather than a possibly stale reporting replica. Monitor replication lag, event backlog, restore success and error rates. Use service identities, encrypted connections, managed secrets, restricted network access, audited permissions and synthetic data for the student lab. Backups require separate retention and restore testing: replicas alone do not protect against replicated deletion.

For a production PostgreSQL alternative, streaming replication is asynchronous by default; unreplicated commits can be lost on failover. Synchronous acknowledgement can reduce that risk but adds waiting and requires a carefully configured failover policy. These are sourced design considerations, not PostgreSQL implementation evidence.

## Sharding proposal, not implemented
Partition customer-owned order data by a stable customer hash. Keep each customer's order and line data colocated; duplicate or centrally serve the small catalogue. Global product inventory and cross-customer reports become coordination problems, so do not shard checkout casually. A customer-key partition does not automatically keep shared-product stock local. Begin with one primary/read replicas unless measured load warrants sharding.

## Availability trade-offs and limitations
The simulated delayed link shows eventual convergence when delivery resumes, not a formal CAP experiment or a network partition benchmark. Keeping a stale replica available for reads sacrifices freshness. A real split-brain prevention policy would fence the old primary and use a promotion coordinator; neither is implemented. All files share one host and failure domain, so this setup provides no host-level high availability. No cloud account, network, automatic failover, consensus, disaster recovery or throughput test is claimed.

A managed cloud deployment could use a private primary plus standby in separate failure domains, automated backups and tested recovery. No deployment is supplied or claimed. The brief explicitly permits a distributed/cloud discussion OR setup.
