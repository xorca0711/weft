"""Bounded discovery batches in the existing discovery store; no scientific dispatch."""
from contextlib import contextmanager
from datetime import date, timedelta
import json
import os
from pathlib import Path

from .discovery import discover, now, write_json
from .europe_pmc import date_window
from .identity import digest


@contextmanager
def exclusive(store):
    """OS-released advisory lock; never break a lock based on elapsed time."""
    path = store.root / '.batch.lock'
    with path.open('a+b') as lock:
        if path.stat().st_size == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError('Discovery batch store is busy; do not break its lock') from exc
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == 'nt':
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def schema(store):
    store.db.executescript('''
      CREATE TABLE IF NOT EXISTS batches(id TEXT PRIMARY KEY, spec_json TEXT NOT NULL, created TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS batch_windows(
        id INTEGER PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batches(id),
        stream TEXT NOT NULL, since_date TEXT NOT NULL, until_date TEXT NOT NULL,
        status TEXT NOT NULL, run_id TEXT, reason TEXT, attempts INTEGER NOT NULL DEFAULT 0,
        UNIQUE(batch_id,stream,since_date,until_date));
      CREATE TABLE IF NOT EXISTS batch_items(
        batch_id TEXT NOT NULL REFERENCES batches(id), candidate_id TEXT NOT NULL REFERENCES candidates(id),
        status TEXT NOT NULL, packet_json TEXT, packet_sha TEXT, source_run TEXT,
        result_json TEXT, reading_json TEXT, reading_result_json TEXT, reason TEXT,
        PRIMARY KEY(batch_id,candidate_id));
      CREATE TABLE IF NOT EXISTS batch_events(
        id INTEGER PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batches(id),
        created TEXT NOT NULL, action TEXT NOT NULL, record_json TEXT NOT NULL);
    ''')


def event(store, batch_id, action, record):
    store.db.execute('INSERT INTO batch_events(batch_id,created,action,record_json) VALUES(?,?,?,?)',
                     (batch_id, now(), action, json.dumps(record)))


def specification(store, batch_id):
    row = store.db.execute('SELECT spec_json FROM batches WHERE id=?', (batch_id,)).fetchone()
    if not row:
        raise ValueError('Unknown batch')
    spec = json.loads(row[0])
    if batch_id != 'batch-' + digest(spec):
        raise ValueError('Batch specification changed')
    return spec


def create(store, context, profile_name, profile, streams, since, until, *,
           max_searches=12, max_records=100, max_screenings=5, max_full_reads=3,
           policy_sha=None):
    schema(store)
    if digest(context['questions']) != context['catalog_sha256']:
        raise ValueError('Context hash mismatch')
    if date.fromisoformat(since) > date.fromisoformat(until):
        raise ValueError('Reversed date window')
    for n, cap in [(max_searches,32),(max_records,200),(max_screenings,20),(max_full_reads,5)]:
        if type(n) is not int or not 1 <= n <= cap:
            raise ValueError('Batch limit outside supported bounds')
    if not streams or len(set(streams)) != len(streams) or 'broad' not in streams:
        raise ValueError('Unique streams including broad required')
    if set(streams) - {'broad','rq_contrary','adjacent_context'} or any(s not in profile['streams'] for s in streams):
        raise ValueError('Batch v1 supports broad/contrary/adjacent streams; no journal-only gate')
    if max_searches < len(streams):
        raise ValueError('Search cap cannot cover even one attempt per stream')
    for stream in streams:
        date_window(profile['streams'][stream], profile['date_field'], since, until)
    spec = dict(schema_version=1, context=context, profile_name=profile_name, profile=profile,
                streams=sorted(streams), since=since, until=until, max_searches=max_searches,
                max_records=max_records, max_screenings=max_screenings, max_full_reads=max_full_reads,
                policy_sha256=policy_sha, selection='paper_key then rq_id; bounded engineering sample, not relevance ranking',
                scientific_execution_allowed=False)
    batch_id = 'batch-' + digest(spec)
    with exclusive(store), store.db:
        old = store.db.execute('SELECT id FROM batches WHERE id=?',(batch_id,)).fetchone()
        if not old:
            store.db.execute('INSERT INTO batches VALUES(?,?,?)',(batch_id,json.dumps(spec),now()))
            for stream in streams:
                store.db.execute('INSERT INTO batch_windows(batch_id,stream,since_date,until_date,status) VALUES(?,?,?,?,?)',
                                 (batch_id,stream,since,until,'pending'))
            event(store,batch_id,'created',{'scope':'discovery only; no scientific job authority'})
    return batch_id


def run(store, batch_id, client=None):
    """Resume only pending windows; errors/unknown outcomes need explicit reconciliation."""
    schema(store)
    with exclusive(store):
        spec = specification(store,batch_id)
        while True:
            used = store.db.execute('SELECT SUM(attempts) FROM batch_windows WHERE batch_id=?',(batch_id,)).fetchone()[0]
            if used >= spec['max_searches']:
                break
            window = store.db.execute("SELECT * FROM batch_windows WHERE batch_id=? AND status='pending' ORDER BY stream,since_date,id LIMIT 1",(batch_id,)).fetchone()
            if not window:
                break
            with store.db:
                store.db.execute("UPDATE batch_windows SET status='running',attempts=attempts+1 WHERE id=?",(window['id'],))
                event(store,batch_id,'search-started',{'window_id':window['id']})
            receipt = discover(store,spec['context'],spec['profile']['streams'][window['stream']],
                               since=window['since_date'],until=window['until_date'],
                               date_field=spec['profile']['date_field'],max_records=spec['max_records'],
                               page_size=min(100,spec['max_records']),client=client)
            status = receipt['status']
            with store.db:
                store.db.execute('UPDATE batch_windows SET status=?,run_id=?,reason=? WHERE id=?',
                                 (status,receipt['run_id'],receipt.get('error'),window['id']))
                event(store,batch_id,'search-returned',{'window_id':window['id'],'run_id':receipt['run_id'],'status':status})
                # Only bounded truncation permits automatic subdivision. An unstable/error result does not.
                if status == 'truncated' and window['since_date'] < window['until_date']:
                    start,end=date.fromisoformat(window['since_date']),date.fromisoformat(window['until_date'])
                    middle=start+(end-start)//2
                    store.db.execute("UPDATE batch_windows SET status='split' WHERE id=?",(window['id'],))
                    for a,b in [(start,middle),(middle+timedelta(days=1),end)]:
                        store.db.execute('INSERT INTO batch_windows(batch_id,stream,since_date,until_date,status) VALUES(?,?,?,?,?)',
                                         (batch_id,window['stream'],a.isoformat(),b.isoformat(),'pending'))
        windows=store.db.execute('SELECT status FROM batch_windows WHERE batch_id=?',(batch_id,)).fetchall()
        if all(w['status'] in {'complete','split'} for w in windows):
            ids=store.db.execute('''SELECT DISTINCT c.id,c.paper_key,c.rq_id FROM candidates c
                JOIN candidate_runs cr ON cr.candidate_id=c.id JOIN batch_windows bw ON bw.run_id=cr.run_id
                WHERE bw.batch_id=? AND bw.status='complete' AND c.current=1
                ORDER BY c.paper_key,c.rq_id''',(batch_id,)).fetchall()
            with store.db:
                for candidate in ids:
                    store.db.execute("INSERT OR IGNORE INTO batch_items(batch_id,candidate_id,status) VALUES(?,?,'queued')",(batch_id,candidate['id']))
    return status_report(store,batch_id)


def reconcile(store,batch_id,window_id,reason):
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError('Explicit reconciliation reason required; inspect the prior attempt first')
    with exclusive(store),store.db:
        specification(store,batch_id)
        row=store.db.execute('SELECT * FROM batch_windows WHERE batch_id=? AND id=?',(batch_id,window_id)).fetchone()
        if not row or row['status'] not in {'running','error','unstable'}:
            raise ValueError('Only interrupted/error/unstable windows can be reconciled')
        event(store,batch_id,'explicit-reconciliation',{'window':dict(row),'reason':reason})
        store.db.execute("UPDATE batch_windows SET status='pending',reason=? WHERE id=?",(reason,window_id))
    return status_report(store,batch_id)


def status_report(store,batch_id):
    from .qualification import summary as evidence_summary
    spec=specification(store,batch_id)
    windows=[dict(r) for r in store.db.execute('SELECT * FROM batch_windows WHERE batch_id=? ORDER BY id',(batch_id,))]
    complete=all(w['status'] in {'complete','split'} for w in windows)
    items=[]
    for row in store.db.execute('''SELECT bi.*,c.paper_key,c.rq_id,c.current,c.status AS candidate_status,c.proposal_json
                                   FROM batch_items bi JOIN candidates c ON c.id=bi.candidate_id
                                   WHERE bi.batch_id=? ORDER BY c.paper_key,c.rq_id''',(batch_id,)):
        result=json.loads(row['result_json']) if row['result_json'] else None
        disposition_current=bool(row['current'])
        if result:
            last=store.db.execute('SELECT record_json FROM events WHERE candidate_id=? ORDER BY id DESC LIMIT 1',(row['candidate_id'],)).fetchone()
            expected={'read_next':'read_next','hold':'held','reject':'rejected'}[result['decision']]
            disposition_current = (disposition_current and row['candidate_status']==expected and
                bool(last) and json.loads(last[0]).get('screening_response_sha256')==digest(result))
        items.append({'candidate_id':row['candidate_id'],'paper_key':row['paper_key'],'rq_id':row['rq_id'],
                      'title':json.loads(row['proposal_json'])['titles'][0],
                      'stage':row['status'] if disposition_current else 'stale','current':bool(row['current']),
                      'disposition_current':disposition_current,'candidate_status':row['candidate_status'],
                      'decision':result['decision'] if result else None,'reason':row['reason'],
                      'reading_status':json.loads(row['reading_json'])['status'] if row['reading_json'] else None,
                      'reading_reviewed':bool(row['reading_result_json']),
                      'evidence_qualification':evidence_summary(store,batch_id,row['candidate_id'])})
    return {'batch_id':batch_id,'discovery_complete':complete,'status':'screening' if complete else 'hold',
            'windows':windows,'candidate_links':len(items),'papers':len({i['paper_key'] for i in items}),
            'limits':{k:v for k,v in spec.items() if k.startswith('max_')},'items':items,
            'screening_complete':complete and all(i['stage'] in {'screened','held','deferred'} for i in items),
            'scientific_execution_allowed':False,'claim_validated':False}


def export_digest(store,batch_id):
    """Fresh immutable digest; private store may contain full text, so no automatic publish."""
    import uuid
    with exclusive(store):
        result=status_report(store,batch_id)
        folder=store.root/('digest-'+uuid.uuid4().hex);folder.mkdir()
        write_json(folder/'digest.json',result)
        lines=['# Weft candidate screening digest','',
               'Agent proposals only. Reading value, data eligibility and RQ support remain separate.','']
        for item in result['items']:
            lines += [f"- {item['title']} ({item['paper_key']}; {item['rq_id']}): {item['stage']}",
                      f"  Decision: {item['decision'] or 'not assessed'}. {item['reason'] or ''}"]
            qualification=item['evidence_qualification']
            if qualification:
                lines.append(f"  Evidence review: {qualification['status']}; current={qualification['current']}; "
                             f"data={qualification.get('data_proposal','unassessed')}; RQ={qualification.get('rq_proposal','unassessed')}.")
        (folder/'digest.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return {'directory':str(folder),'digest_sha256':digest(result),'candidate_links':len(result['items']),
                'scientific_execution_allowed':False}
