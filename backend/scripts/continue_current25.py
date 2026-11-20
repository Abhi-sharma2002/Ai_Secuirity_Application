"""Explicit Oct30 continuation: only untouched main rows, never previous attempts."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.evaluation import current25_continuation_scope as scope
from app.evaluation.suite_context import continuation_suite
from app.evaluation.simple_config import load_config, EvaluationError
from scripts.run_eval import _run, _read_rows, COLUMNS

BASE=ROOT/'results/current25'
PRIOR=BASE/'runs/main-20261029-v1'
OUT=BASE/'continuations/untouched-20261030-v2'


def atomic(path, value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as handle:
        handle.write(value);handle.flush();os.fsync(handle.fileno())
    tmp.replace(path)


def aggregate():
    receipt=json.loads(scope.SCOPE.read_text())
    if hashlib.sha256((PRIOR/'records.csv').read_bytes()).hexdigest()!=receipt['prior_records_sha256']:
        raise EvaluationError('Frozen previous records changed')
    rows=[]
    for folder in (PRIOR,OUT):
        path=folder/'records.csv'
        if path.exists():
            with path.open(newline='') as handle:rows.extend(csv.DictReader(handle))
    keys=[(r['case_id'],r['mode']) for r in rows]
    if len(keys)!=len(set(keys)):raise EvaluationError('Duplicate rows in aggregate')
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=COLUMNS,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    for path in (OUT/'retrieval').glob('*.json'):
        dest=BASE/'retrieval'/path.name
        if dest.exists() and dest.read_bytes()!=path.read_bytes():
            raise EvaluationError('Frozen retrieval differs')
        if not dest.exists():shutil.copy2(path,dest)
    old=json.loads((PRIOR/'run_metadata.json').read_text())
    new=json.loads((OUT/'run_metadata.json').read_text()) if (OUT/'run_metadata.json').exists() else {}
    metadata={**old,'origin':'azure_live_current25_aggregate_with_explicit_continuation',
        'implementation_history':[{'scope':'user-approved-current25-main-20261029-v1','metadata':str((PRIOR/'run_metadata.json').relative_to(ROOT)),'records_sha256':receipt['prior_records_sha256']},
                                  {'scope':scope.AUTHORIZATION,'metadata':str((OUT/'run_metadata.json').relative_to(ROOT)),'implementation_sha256':receipt['implementation_sha256']}],
        'row_provenance':{f'{r["case_id"]}/{r["mode"]}':('user-approved-current25-main-20261029-v1' if i<19 else scope.AUTHORIZATION) for i,r in enumerate(rows)},
        'note':'Derived aggregate; original raw observations are preserved in independent run directories. Error-handling continuation is not one unchanged execution.'}
    atomic(BASE/'run_metadata.json',json.dumps(metadata,indent=2)+'\n')
    atomic(BASE/'records.csv',stream.getvalue())


def prepare(config,data,manifest_sha):
    from app.llm import client
    from app.evaluation.simple_runner import _identity
    if scope.SCOPE.exists() or PRIOR.exists() or OUT.exists():
        raise EvaluationError('Continuation already prepared; no renewal or overwrite')
    approved=client.approval();capacity=client.allowance_capacity(approved)
    if capacity['stopped'] or capacity['remaining_calls']<163 or capacity['remaining_reserved_tokens']<5216000:
        raise EvaluationError('Existing allowance cannot fund approved ceiling')
    rows=_read_rows(BASE/'records.csv',data,config)
    if len(rows)!=19:raise EvaluationError('Expected exactly 19 previous rows')
    identity=_identity(config,manifest_sha)
    PRIOR.mkdir(parents=True)
    for path in BASE.iterdir():
        if path.name in ('runs','continuations') or path.name.startswith('.'):continue
        if path.is_dir():shutil.copytree(path,PRIOR/path.name)
        else:shutil.copy2(path,PRIOR/path.name)
    allowed=sorted({(c['case_id'],m) for c in data['cases'] for m in 'ABC'}-set(rows))
    if len(allowed)!=122:raise EvaluationError('Untouched row count differs')
    receipt=dict(authorization=scope.AUTHORIZATION,max_calls=163,max_reservation_units=5216000,
        expires_at=None,config=config,manifest_sha256=manifest_sha,implementation_sha256=scope.implementation_hash(),
        parent_allowance_id=approved.allowance_id,user_confirmed_trial_credits_and_quota=True,
        cases=[c['case_id'] for c in data['cases']],allowed_rows=allowed,continue_content_filter_errors=True,
        prior_records=str((PRIOR/'records.csv').relative_to(ROOT)),prior_records_sha256=hashlib.sha256((PRIOR/'records.csv').read_bytes()).hexdigest(),
        index_identity=identity,created_at=datetime.now(timezone.utc).isoformat(),
        user_instruction='Remaining main benchmark only: 122 rows, at most 163 calls; provider content-filter errors may advance to distinct untouched rows; no retries/fallback/filter changes; stop on other operational failure.',
        preflight_remaining_calls=capacity['remaining_calls'])
    fd=os.open(scope.SCOPE,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as handle:json.dump(receipt,handle,indent=2);handle.write('\n')
    return dict(prepared=True,untouched_rows=122,max_calls=163,remaining_calls=capacity['remaining_calls'],provider_requests_made=0)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    from app.core.environment import load_environment
    load_environment()
    with continuation_suite():
        from app.evaluation.simple_runner import _manifest
        config=load_config();data,manifest_sha=_manifest()
        if args.prepare:
            print(json.dumps(prepare(config,data,manifest_sha)));return
        if not args.live:parser.error('Choose --prepare or --live')
        scope.validate(config)
        if os.getenv('LIVE_LLM_ENABLED')!='true' or os.getenv('LIVE_EVALUATION_ENABLED')!='true':
            raise EvaluationError('Explicit process live flags required')
        if OUT.exists():raise EvaluationError('Continuation already attempted; no automatic resume')
        os.environ['EVAL_MODE']='1'
        old=_read_rows(PRIOR/'records.csv',data,config)
        try:
            result=_run(data,config,manifest_sha,output=OUT,origin='azure_live_current25_untouched_v2',skip_keys=set(old),on_record=aggregate,evidence_seed=PRIOR/"retrieval")
            aggregate();scope.CLOSED.touch(exist_ok=False)
            print(json.dumps(result),flush=True)
        except BaseException:
            scope.stop();raise
        finally:
            if (OUT/'records.csv').exists():
                aggregate()
                from app.evaluation.current25 import refresh_report
                print(json.dumps(refresh_report()),flush=True)
            calls=len(scope.JOURNAL.read_text().splitlines()) if scope.JOURNAL.exists() else 0
            atomic(ROOT/'docs/current25/CONTINUATION_OUTCOME.json',json.dumps(dict(scope=scope.AUTHORIZATION,calls=calls,closed=scope.CLOSED.exists(),stopped=scope.STOP.exists(),timestamp=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')

if __name__=='__main__':main()
