import json
from app.storage import registry as reg
from app.evaluation import upload_observations


def test_upload_results_exclude_old_versions_and_predefined_without_grading(tmp_path,monkeypatch):
    monkeypatch.setattr(reg,'ROOT',tmp_path)
    reg.initialize()
    monkeypatch.setattr(upload_observations.lifecycle,'snapshot',lambda:[dict(document_id='upload',id='new',filename='invoice.pdf')])
    def response(doc,version):
        return dict(mode='A',status='answered',answer='Saved answer',candidate_evidence=[dict(document_id=doc,version_id=version,filename='invoice.pdf')])
    with reg.connect() as db:
        for key,result in [('valid',response('upload','new')),('old',response('upload','old')),('predefined',response('development-01','v1')),
                           ('mixed',dict(results={'B':response('upload','new'),'C':response('upload','old')}))]:
            db.execute('INSERT INTO requests VALUES(?,?,?)',(key,'test',json.dumps(result)))
    value=upload_observations.snapshot()
    assert value['document_count']==1 and value['provider_calls']==0
    assert [(r['request_id'],r['mode']) for r in value['observations']]==[('valid','A'),('mixed','B')]
    assert all(r['human_quality'] is None and r['attack_succeeded'] is None and r['task_correct'] is None for r in value['observations'])
