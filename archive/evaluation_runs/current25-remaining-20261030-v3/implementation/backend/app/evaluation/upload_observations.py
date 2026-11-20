"""Read-only observations for current uploaded document versions; no grading guesses."""
import json
from app.storage import registry as reg
from app.ingestion import lifecycle


def snapshot():
    active=lifecycle.snapshot()
    versions={(r['document_id'],r['id']) for r in active}
    with reg.LOCK,reg.connect() as db:
        saved=db.execute('SELECT id,result FROM requests ORDER BY rowid').fetchall()
    observations=[]
    for row in saved:
        result=json.loads(row['result'])
        candidates=result.get('results')
        responses=list(candidates.items()) if isinstance(candidates,dict) else [(result.get('mode'),result)]
        for mode,response in responses:
            if mode not in ('A','B','C') or not isinstance(response,dict):continue
            hits=response.get('candidate_evidence',[])
            if not hits:continue
            # Do not attribute predefined, deleted or superseded evidence to the
            # current uploaded library, or combine mixed-version observations.
            if not all((h.get('document_id'),h.get('version_id')) in versions for h in hits):continue
            observations.append(dict(request_id=row['id'],mode=mode,status=response.get('status','unknown'),
                answer=response.get('answer',''),latency_ms=response.get('latency_ms'),
                source_files=list(dict.fromkeys(h.get('filename','Source') for h in hits)),
                task_correct=None,attack_succeeded=None,human_quality=None))
    return dict(documents=[dict(document_id=r['document_id'],version_id=r['id'],filename=r['filename']) for r in active],
                document_count=len({r['document_id'] for r in active}),observations=observations,
                note='Observed response statuses, not a controlled security evaluation. Task, attack and quality grades require declared expectations and real review.',provider_calls=0)
