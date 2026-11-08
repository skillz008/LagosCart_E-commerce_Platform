from pathlib import Path
import sqlite3, random, datetime, time, statistics, json, csv, platform, sys, importlib.util
ROOT=Path(__file__).resolve().parent
P1=ROOT/'portfolio-1-database-design'; P2=ROOT/'portfolio-2-query-optimisation'; P3=ROOT/'portfolio-3-transactions-concurrency'; P4=ROOT/'portfolio-4-nosql'; P5=ROOT/'portfolio-5-distributed-cloud'
R=ROOT/'runtime'; R.mkdir(exist_ok=True)
for p in R.glob('*'):
    if p.is_file(): p.unlink()
def connect(path):
    c=sqlite3.connect(path,timeout=0.15,isolation_level=None)
    c.execute('PRAGMA foreign_keys=ON'); return c
def write(path,obj): path.write_text(json.dumps(obj,indent=2,default=str))
c=connect(R/'lagoscart.db'); c.executescript((P1/'schema.sql').read_text()); c.execute('PRAGMA journal_mode=WAL')
rng=random.Random(8103); c.execute('BEGIN')
c.executemany('INSERT INTO customers VALUES(?,?,?)',[(i,f'Customer {i}',f'customer{i}@example.invalid') for i in range(1,2001)])
c.executemany('INSERT INTO categories VALUES(?,?)',[(1,'Electronics'),(2,'Fashion'),(3,'Home')])
products=[(i,(i-1)%3+1,f'SKU-{i:04}',f'Product {i}',rng.randrange(1000,100000)*100,rng.randrange(0,201)) for i in range(1,301)]
c.executemany('INSERT INTO products VALUES(?,?,?,?,?,?)',products)
orders=[]; items=[]; payments=[]; deliveries=[]
for i in range(1,100001):
    status=rng.choice(['pending','paid','shipped','cancelled']); customer=rng.randrange(1,1901)
    date=(datetime.date(2026,1,1)+datetime.timedelta(days=rng.randrange(300))).isoformat()
    orders.append((i,customer,date,status)); total=0
    for pid in rng.sample(range(1,301),rng.randrange(1,4)):
        qty=rng.randrange(1,4); price=products[pid-1][4]; total+=qty*price; items.append((i,pid,qty,price))
    if status in ('paid','shipped'): payments.append((i,i,f'PAY-{i:06}',total,'captured'))
    if status=='shipped': deliveries.append((i,i,f'Synthetic address {customer}, Lagos','dispatched'))
c.executemany('INSERT INTO orders VALUES(?,?,?,?)',orders); c.executemany('INSERT INTO order_items VALUES(?,?,?,?)',items)
c.executemany('INSERT INTO payments VALUES(?,?,?,?,?)',payments); c.executemany('INSERT INTO deliveries VALUES(?,?,?,?)',deliveries); c.execute('COMMIT')
counts={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['customers','categories','products','orders','order_items','payments','deliveries']}
write(P1/'data-profile.json',counts)
q='SELECT order_id,ordered_at,status FROM orders WHERE customer_id=? AND ordered_at>=? ORDER BY ordered_at DESC'
args=(42,'2026-04-01')
def benchmark():
    plan=c.execute('EXPLAIN QUERY PLAN '+q,args).fetchall()
    for _ in range(3): c.execute(q,args).fetchall()
    times=[]
    for _ in range(31):
        t=time.perf_counter_ns(); rows=c.execute(q,args).fetchall(); times.append((time.perf_counter_ns()-t)/1e6)
    return plan,times,rows
before,bt,br=benchmark(); c.executescript((P2/'indexes.sql').read_text()); after,at,ar=benchmark(); assert br==ar
result={'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'platform':platform.platform(),'seed':8103,'row_counts':counts,'warmups':3,'repetitions':31,'rows_returned':len(ar),'before_plan':before,'after_plan':after,'before_median_ms':statistics.median(bt),'after_median_ms':statistics.median(at),'speedup':statistics.median(bt)/statistics.median(at),'identical_results':br==ar}
write(P2/'benchmark.json',result)
with (P2/'timings.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['run','before_ms','after_ms']); w.writerows((i+1,b,a) for i,(b,a) in enumerate(zip(bt,at)))
query_text='\n'.join(line for line in (P2/'queries.sql').read_text().splitlines() if not line.lstrip().startswith('--'))
queries=[s.strip() for s in query_text.split(';') if s.strip()]
outputs=[]
for i,sql in enumerate(queries,1):
    cur=c.execute(sql); rows=cur.fetchall()
    with (P2/f'query-{i}-results.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow([d[0] for d in cur.description]); w.writerows(rows)
    outputs.append({'query':i,'rows':len(rows),'plan':c.execute('EXPLAIN QUERY PLAN '+sql).fetchall()})
write(P2/'all-query-plans.json',outputs)
checks=[]
def check(name,ok,detail):
    assert ok,name; checks.append({'test':name,'passed':bool(ok),'detail':detail})
for name,sql in [('unique_email',"INSERT INTO customers VALUES(9999,'Duplicate','customer1@example.invalid')"),('negative_stock','UPDATE products SET stock=-1 WHERE product_id=1'),('foreign_key',"INSERT INTO orders VALUES(999999,99999,'2026-01-01','pending')")]:
    try: c.execute(sql); ok=False
    except sqlite3.IntegrityError as e: ok=True; detail=str(e)
    check(name,ok,detail)
check('foreign_key_check',c.execute('PRAGMA foreign_key_check').fetchall()==[],'No violations')
check('integrity_check',c.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity_check=ok')
write(P1/'constraint-tests.json',checks); checks=[]
c.execute('UPDATE products SET stock=1 WHERE product_id=1')
c.execute('BEGIN IMMEDIATE'); c.execute('UPDATE products SET stock=0 WHERE product_id=1'); c.execute('ROLLBACK')
check('rollback',c.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==1,'Stock restored to 1')
a=connect(R/'lagoscart.db'); b=connect(R/'lagoscart.db')
a.execute('BEGIN IMMEDIATE'); a.execute('UPDATE products SET stock=0 WHERE product_id=1')
check('no_dirty_read',b.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==1,'Other connection sees committed stock=1')
try: b.execute('BEGIN IMMEDIATE'); locked=False
except sqlite3.OperationalError as e: locked='locked' in str(e); detail=str(e)
check('writer_contention',locked,detail); a.execute('ROLLBACK')
a.execute('BEGIN'); old=a.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]
b.execute('BEGIN IMMEDIATE'); b.execute('UPDATE products SET stock=2 WHERE product_id=1'); b.execute('COMMIT')
check('snapshot',a.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==old,'Reader remains at 1 while committed writer sets 2')
a.execute('COMMIT'); check('snapshot_refresh',a.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==2,'New read sees 2'); a.close(); b.close()
c.execute('UPDATE products SET stock=1 WHERE product_id=1')
c.executescript((P3/'checkout.sql').read_text())
check('checkout_commit',c.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==0 and c.execute('SELECT COUNT(*) FROM payments WHERE order_id=100001').fetchone()[0]==1,'Order, line, payment and decrement committed')
c.execute('BEGIN IMMEDIATE'); changed=c.execute('UPDATE products SET stock=stock-1 WHERE product_id=1 AND stock>=1').rowcount; c.execute('ROLLBACK')
check('overselling_prevented',changed==0,'Second buyer affects zero rows and must stop')
initial=c.execute('SELECT stock FROM products WHERE product_id=2').fetchone()[0]
c.execute('BEGIN IMMEDIATE'); c.execute('UPDATE products SET stock=stock+1 WHERE product_id=2')
try: c.execute("INSERT INTO customers VALUES(1,'Bad','bad@example.invalid')")
except sqlite3.IntegrityError: c.execute('ROLLBACK')
check('failure_atomicity',c.execute('SELECT stock FROM products WHERE product_id=2').fetchone()[0]==initial,'Later constraint failure followed by explicit rollback restores earlier change')
write(P3/'transaction-tests.json',checks)
spec=importlib.util.spec_from_file_location('document_store',P4/'document_store.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
store=mod.DocumentStore(R/'catalogue.json')
store.insert({'_id':'SKU-0001','name':'Android Phone','category':'Electronics','price_kobo':12500000,'attributes':{'ram_gb':8,'storage_gb':128},'variants':[{'colour':'black','sku':'PHONE-BLK'}]})
store.insert({'_id':'SKU-0002','name':'Cotton Shirt','category':'Fashion','price_kobo':1800000,'attributes':{'size':'L','fabric':'cotton'}})
store.update('SKU-0001',{'network':'5G'})
reloaded=mod.DocumentStore(R/'catalogue.json'); assert reloaded.find('Electronics')[0]['attributes']['network']=='5G'
try: reloaded.insert(reloaded.docs['SKU-0001']); duplicate=False
except ValueError: duplicate=True
assert duplicate
reloaded.insert({'_id':'TEMP','category':'Test','attributes':{}}); reloaded.delete('TEMP'); assert 'TEMP' not in mod.DocumentStore(R/'catalogue.json').docs
write(P4/'catalogue-example.json',reloaded.docs)
write(P4/'document-tests.json',{'insert':True,'find':True,'update':True,'reload_persistence':True,'duplicate_rejected':duplicate,'delete':True,'electronics_result':reloaded.find('Electronics'),'engine':'Custom single-process JSON document store; not MongoDB'})
# Independent local files model nodes; delivery is explicit, not a network service.
primary=connect(R/'primary.db'); replica=connect(R/'replica.db')
primary.executescript('CREATE TABLE catalogue(id INTEGER PRIMARY KEY, stock INTEGER); CREATE TABLE outbox(seq INTEGER PRIMARY KEY AUTOINCREMENT,id INTEGER,stock INTEGER);')
replica.executescript('CREATE TABLE catalogue(id INTEGER PRIMARY KEY, stock INTEGER); CREATE TABLE applied(seq INTEGER PRIMARY KEY);')
def publish(stock):
    primary.execute('BEGIN IMMEDIATE'); primary.execute('INSERT INTO catalogue VALUES(1,?) ON CONFLICT(id) DO UPDATE SET stock=excluded.stock',(stock,)); primary.execute('INSERT INTO outbox(id,stock) VALUES(1,?)',(stock,)); primary.execute('COMMIT')
def deliver():
    for seq,pid,stock in primary.execute('SELECT seq,id,stock FROM outbox ORDER BY seq'):
        replica.execute('BEGIN IMMEDIATE')
        if replica.execute('SELECT 1 FROM applied WHERE seq=?',(seq,)).fetchone() is None:
            replica.execute('INSERT INTO catalogue VALUES(?,?) ON CONFLICT(id) DO UPDATE SET stock=excluded.stock',(pid,stock)); replica.execute('INSERT INTO applied VALUES(?)',(seq,))
        replica.execute('COMMIT')
publish(10); deliver(); publish(9)
stale=replica.execute('SELECT stock FROM catalogue').fetchone()[0]; fresh=primary.execute('SELECT stock FROM catalogue').fetchone()[0]
assert (stale,fresh)==(10,9)
deliver(); converged=replica.execute('SELECT stock FROM catalogue').fetchone()[0]; deliver()
assert converged==9 and replica.execute('SELECT COUNT(*) FROM applied').fetchone()[0]==2
publish(8); primary.close()
standby=replica.execute('SELECT stock FROM catalogue').fetchone()[0]; assert standby==9
write(P5/'replication-tests.json',{'local_simulation':True,'paused_delivery_primary_stock':fresh,'paused_delivery_replica_stock':stale,'after_catchup_stock':converged,'duplicate_delivery_applied_count':2,'primary_unavailable_replica_read':standby,'unreplicated_primary_value':8,'promotion_performed':False,'interpretation':'Read availability with stale data; no automatic failover, network or consensus implemented.'})
replica.close(); c.execute('PRAGMA wal_checkpoint(TRUNCATE)'); c.close()
write(ROOT/'documentation'/'execution-manifest.json',{'environment':result,'tests':'All assertions completed successfully','scope':'SQLite relational tests, custom JSON document store, local application-level replication simulation','not_executed':['MongoDB optional script','cloud deployment','GitHub actions','LMS submission']})
print(json.dumps(result,indent=2))
