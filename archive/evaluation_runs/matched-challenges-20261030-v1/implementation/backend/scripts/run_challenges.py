"""Independent 8-case, 32-call experiment; never alters the main benchmark."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'backend'))
from app.evaluation import challenge_scope as scope
from app.evaluation.challenges import definitions,RESULTS,grade,ERRORS,snapshot
from app.evaluation.simple_config import load_config
from app.evaluation.suite_context import challenge_suite


def evaluation_call(config,hits):
    from app.evaluation.simple_runner import _invoke_model,_ScreeningWithReasons
    from app.evaluation.simple_config import EvaluationError
    def call(messages,schema,stage,reservation):
        wire=_ScreeningWithReasons.model_json_schema() if stage=='screening' else schema
        raw,trace=_invoke_model(messages,wire,stage,config)
        if stage=='screening':
            decision=_ScreeningWithReasons.model_validate_json(raw)
            if (not set(decision.flagged_source_ids)<={h['id'] for h in hits}
                or set(decision.source_reasons)!=set(decision.flagged_source_ids)
                or any(not r.strip() for r in decision.source_reasons.values())
                or (decision.question_flagged and not decision.question_reason.strip())
                or (not decision.question_flagged and decision.question_reason.strip())):
                raise EvaluationError('Invalid screening reasons or source IDs')
            raw=decision.model_dump_json(exclude={'question_reason','source_reasons'})
        return raw,trace
    return call


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--live',action='store_true');args=parser.parse_args()
    from app.core.environment import load_environment
    from app.llm import client
    load_environment();data=definitions();config=load_config()
    binding=hashlib.sha256((ROOT/'backend/benchmark_challenges/manifest.json').read_bytes()).hexdigest()
    if args.prepare:
        if scope.SCOPE.exists() or RESULTS.exists():raise ValueError('Scope already prepared or observations exist; no renewal')
        approved=client.approval();capacity=client.allowance_capacity(approved)
        if capacity['stopped'] or capacity['remaining_calls']<32 or capacity['remaining_reserved_tokens']<1024000:raise ValueError('Insufficient existing allowance')
        receipt=dict(authorization=scope.AUTHORIZATION,max_calls=32,max_reservation_units=1024000,expires_at=None,
            config=config,manifest_sha256=binding,implementation_sha256=scope.implementation_hash(),parent_allowance_id=approved.allowance_id,
            user_confirmed_trial_credits_and_quota=True,cases=[c['case_id'] for c in data['cases']],allowed_rows=[[c['case_id'],m] for c in data['cases'] for m in 'ABC'],
            user_instruction='Run the 8 new cases, capped at 32 calls; existing trial allowance only; no retries/fallback/expiry; stop on first operational failure.')
        with os.fdopen(os.open(scope.SCOPE,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as handle:json.dump(receipt,handle,indent=2)
        print(json.dumps(dict(prepared=True,cases=8,max_calls=32,provider_calls=0)));return
    if not args.live:parser.error('Select --prepare or --live')
    if os.getenv('LIVE_EVALUATION_ENABLED')!='true' or os.getenv('LIVE_LLM_ENABLED')!='true':raise ValueError('Explicit live process flags required')
    def interrupted(*args):raise InterruptedError('Interrupted challenge execution')
    signal.signal(signal.SIGTERM,interrupted)
    with challenge_suite():
        scope.validate(config)
        if RESULTS.exists():raise ValueError('Already attempted; no automatic replay')
        RESULTS.mkdir(parents=True)
        os.environ['EVAL_MODE']='1'
        from app.evaluation.simple_runner import _invoke_model,_error_text
        from app.rag.assistant import respond
        try:
            for case in data['cases']:
                for mode in 'ABC':
                    scope.check_row(case['case_id'],mode,config)
                    hit=dict(id=case['case_id']+'-source',document_id=case['case_id'],filename=case['document_path'],text=case['source_text'],page=0,section='policy')
                    call=evaluation_call(config,[hit])
                    try:
                        with scope.row(case['case_id'],mode):
                            result=respond(case['query'],mode,initial={'hits':[hit],'snapshot':[],'omitted_ids':[]},_evaluation_call=call)
                    except Exception as exc:
                        result=dict(status='operational_error',answer='',error=_error_text(exc),calls=[])
                    row=dict(case_id=case['case_id'],mode=mode,manifest_sha256=binding,response=result,status=result['status'],answer=result.get('answer',''),grades=grade(case,mode,result))
                    with (RESULTS/f'{case["case_id"]}--{mode}.json').open('x') as handle:
                        json.dump(row,handle,indent=2);handle.flush();os.fsync(handle.fileno())
                    if result['status'] in ERRORS:raise ValueError('Challenge run stopped on first operational failure; saved row preserved')
            scope.CLOSED.touch(exist_ok=False)
        except BaseException:
            scope.stop();raise
        finally:
            count=len(scope.JOURNAL.read_text().splitlines()) if scope.JOURNAL.exists() else 0
            (ROOT/'docs/current25/CHALLENGE_OUTCOME.json').write_text(json.dumps(dict(calls=count,closed=scope.CLOSED.exists(),stopped=scope.STOP.exists(),recorded_rows=snapshot()['recorded_rows'],timestamp=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
        print(json.dumps(snapshot()['summary']))

if __name__=='__main__':main()
