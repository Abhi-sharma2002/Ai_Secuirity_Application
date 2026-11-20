"""Frozen all-upload validation, requiring independent explicit sensitive-data approval."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'backend'))
from app.evaluation import upload_validation_last_scope as scope
from app.evaluation.suite_context import upload_validation_last_suite
from app.evaluation.simple_config import load_config,EvaluationError
INPUT=ROOT/'.private/all_uploads_validation_20261030_v1_inputs.json'
OUTPUT=ROOT/'results/upload_validation_20261030_v4'


def write(path,data):
    with path.open('x') as handle:
        json.dump(data,handle,indent=2);handle.flush();os.fsync(handle.fileno())


def check_versions(plan):
    from app.ingestion.lifecycle import snapshot
    active={r['document_id']:r for r in snapshot()}
    for doc in plan['documents']:
        item=active.get(doc['document_id'])
        if not item or item['id']!=doc['version_id'] or item['sha256']!=doc['sha256']:
            raise EvaluationError('An approved document was deleted or replaced; no further calls')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-approved',action='store_true');parser.add_argument('--live',action='store_true');args=parser.parse_args()
    from app.core.environment import load_environment
    from app.llm import client
    load_environment();inputs=json.loads(INPUT.read_text());plan=inputs['plan'];config=load_config();check_versions(plan)
    if args.prepare_approved:
        if scope.SCOPE.exists() or OUTPUT.exists():raise EvaluationError('Already prepared/attempted; no renewal')
        approved=client.approval();capacity=client.allowance_capacity(approved)
        if capacity['stopped'] or capacity['remaining_calls']<12 or capacity['remaining_reserved_tokens']<384000:raise EvaluationError('Insufficient existing capacity')
        receipt=dict(authorization=scope.AUTHORIZATION,max_calls=12,max_reservation_units=384000,expires_at=None,
            prior_rows_sha256=scope.prior_hash(),config=config,manifest_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),implementation_sha256=scope.implementation_hash(),
            parent_allowance_id=approved.allowance_id,user_confirmed_trial_credits_and_quota=True,
            cases=[c['case_id'] for c in plan['cases']],allowed_rows=scope.untouched_rows(plan),
            sensitive_payload_explicitly_approved=True,continue_content_filter_errors=True,
            user_instruction='Approve 2000-token shared A/B/C cap and only final 9 untouched rows, at most 12 calls; required citation schema; all 10 frozen uploads including full cards and personal/sensitive passages sent to existing Azure deployment; no retry/fallback/expiry; advance only filter refusals, stop on other errors.')
        with os.fdopen(os.open(scope.SCOPE,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as handle:json.dump(receipt,handle,indent=2)
        print(json.dumps({'prepared':True,'documents':10,'rows':9,'max_calls':12,'provider_calls':0}));return
    if not args.live:parser.error('Select --prepare-approved or --live')
    if os.getenv('LIVE_EVALUATION_ENABLED')!='true' or os.getenv('LIVE_LLM_ENABLED')!='true':raise EvaluationError('Explicit process live flags required')
    def interrupt(*args):raise InterruptedError('Validation interrupted; no automatic replay')
    signal.signal(signal.SIGTERM,interrupt)
    from scripts.run_challenges_remaining import evaluation_call
    from app.rag.assistant import respond
    from app.defenses.output_screening import contains_payment_card
    from app.evaluation.simple_runner import _error_text
    errors={'error','operational_error','llm_error','screening_error','invalid_citations','live_blocked'}
    with upload_validation_last_suite():
        scope.validate(config)
        if OUTPUT.exists():raise EvaluationError('Already attempted; no automatic replay')
        OUTPUT.mkdir(parents=True);os.environ['EVAL_MODE']='1'
        try:
            for check in inputs['checks']:
                case=check['case'];initial=check['initial']
                allowed={r['document_id'] for r in initial['snapshot']}
                for mode in 'ABC':
                    if [case['case_id'],mode] not in scope.untouched_rows(plan):continue
                    check_versions(plan);scope.check_row(case['case_id'],mode,config)
                    try:
                        with scope.row(case['case_id'],mode):
                            result=respond(case['question'],mode,initial=initial,_evaluation_call=evaluation_call(config,initial['hits']))
                    except Exception as exc:result={'status':'operational_error','answer':'','error':_error_text(exc),'calls':[]}
                    refs=result.get('references',[])
                    row=dict(case_id=case['case_id'],kind=case['kind'],document_id=case['document_id'],mode=mode,status=result['status'],
                        error=result.get('error'),calls=len(result.get('calls',[])),latency_ms=result.get('latency_ms'),
                        retrieved_documents=list(dict.fromkeys(h['document_id'] for h in initial['hits'])),
                        cited_documents=list(dict.fromkeys(h['document_id'] for h in refs)),
                        citations_in_approved_scope=all(h['document_id'] in allowed for h in refs) if refs else None,
                        full_card_in_delivered_answer=contains_payment_card(result.get('answer','')),
                        answer_sha256=hashlib.sha256(result.get('answer','').encode()).hexdigest(),
                        unsupported_answer_abstained=result['status']=='insufficient_evidence' if case['kind']=='unsupported' else None,
                        screening=result.get('screening'),semantic_quality=None,human_reviewer=None)
                    write(OUTPUT/f'{case["case_id"]}--{mode}.json',row)
                    if result['status'] in errors:
                        if scope.may_continue(result.get('error') or ''):continue
                        raise EvaluationError('Upload validation stopped on non-filter operational error; row saved; no retry')
            scope.CLOSED.touch(exist_ok=False)
        except BaseException:
            scope.stop();raise
        finally:
            rows=[json.loads(p.read_text()) for p in OUTPUT.glob('*.json')]
            count=len(scope.JOURNAL.read_text().splitlines()) if scope.JOURNAL.exists() else 0
            summary=dict(documents=10,planned_rows=9,recorded_rows=len(rows),unrun_rows=9-len(rows),calls=count,
                closed=scope.CLOSED.exists(),stopped=scope.STOP.exists(),errors=sum(r['status'] in errors for r in rows),
                raw_card_disclosures=sum(r['full_card_in_delivered_answer'] for r in rows),
                wrong_scope_citations=sum(r['citations_in_approved_scope'] is False for r in rows),
                human_quality_ratings=0,timestamp=datetime.now(timezone.utc).isoformat())
            write(ROOT/'.cache/all_uploads_validation_last_outcome.json',summary)
            print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
