"""Independent user-approved 32-call matched-challenge scope; existing aggregate Azure ledger only."""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
import hashlib
import json
import os
from app.evaluation.simple_config import ROOT, EvaluationError

AUTHORIZATION = 'user-approved-matched-challenges-20261030-v1'
SCOPE = ROOT/'.private/matched_challenges_20261030_v1.json'
JOURNAL = ROOT/'.private/matched_challenges_20261030_v1_attempts.jsonl'
STOP = ROOT/'.private/matched_challenges_20261030_v1.stopped'
CLOSED = ROOT/'.private/matched_challenges_20261030_v1.closed'
ROW = ContextVar('current25_execution_row', default=None)


def implementation_hash():
    files = [ROOT/'backend/scripts/run_challenges.py']
    for folder in ('defenses','rag','llm','evaluation'):
        files.extend((ROOT/'backend/app'/folder).glob('*.py'))
    return hashlib.sha256(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(files)},sort_keys=True).encode()).hexdigest()


def stop():
    STOP.touch(exist_ok=True)


def may_continue(error):
    return False


def validate(config):
    from app.llm import client
    try:
        scope = json.loads(SCOPE.read_text())
        approved = client.approval()
        from app.evaluation.challenges import definitions
        data = definitions()
        manifest_sha = hashlib.sha256((ROOT/'backend/benchmark_challenges/manifest.json').read_bytes()).hexdigest()
        if (scope['authorization'] != AUTHORIZATION or scope['max_calls'] != 32
                or scope['max_reservation_units'] != 1024000 or scope['expires_at'] is not None
                or scope['config'] != config or scope['manifest_sha256'] != manifest_sha
                or scope['implementation_sha256'] != implementation_hash()
                or scope['parent_allowance_id'] != approved.allowance_id
                or not scope['user_confirmed_trial_credits_and_quota']
                or scope['cases'] != [c['case_id'] for c in data['cases']]
                or scope['allowed_rows'] != [[c['case_id'],m] for c in data['cases'] for m in 'ABC']
                or data['version'] != 'matched-challenges-v1'
                or approved.provider != 'azure_openai' or not approved.confirmed_free_promotional
                or approved.paid_azure_test_authorized):
            raise ValueError()
    except Exception:
        raise EvaluationError('The current25 dataset has no live benchmark authorization matching these inputs; no request sent.') from None
    if STOP.exists() or CLOSED.exists():
        raise EvaluationError('Current25 scope is stopped or closed; no request sent.')
    capacity = client.allowance_capacity(approved)
    if capacity['stopped']:
        raise EvaluationError('Existing aggregate allowance is stopped; no request sent.')
    return scope, capacity


@contextmanager
def row(case_id, mode):
    token = ROW.set((case_id, mode))
    try:
        yield
    finally:
        ROW.reset(token)


def check_row(case_id, mode, config):
    scope, capacity = validate(config)
    if [case_id, mode] not in scope['allowed_rows']:
        raise EvaluationError('Row outside the approved current25 main benchmark')
    needed = 2 if mode == 'C' else 1
    attempts = [json.loads(line) for line in JOURNAL.read_text().splitlines()] if JOURNAL.exists() else []
    if (len(attempts)+needed > scope['max_calls'] or capacity['remaining_calls'] < needed
            or capacity['remaining_reserved_tokens'] < needed*32000):
        stop()
        raise EvaluationError('Capacity cannot fund this row maximum; untouched rows remain unrun.')


def invoke(messages, schema, stage, config):
    from app.llm import client
    scope, _ = validate(config)
    selected = ROW.get()
    if selected is None:
        raise EvaluationError('Current25 provider call requires an approved execution row')
    case_id, mode = selected
    if [case_id, mode] not in scope['allowed_rows'] or stage not in ('screening','generation') or (stage=='screening' and mode!='C'):
        raise EvaluationError('Provider stage outside the approved workload')
    JOURNAL.parent.mkdir(parents=True,exist_ok=True)
    with JOURNAL.open('a+') as handle:
        fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
        handle.seek(0)
        attempts=[json.loads(line) for line in handle if line.strip()]
        key=(case_id,mode,stage)
        if (STOP.exists() or CLOSED.exists() or len(attempts)>=32
                or any((a['case_id'],a['mode'],a['stage'])==key for a in attempts)):
            raise EvaluationError('Scope stopped, closed, exhausted or stage already attempted; no retry.')
        try:
            reservation=client.reserve(1,32000,metadata={'experiment_id':AUTHORIZATION,
                'case_id':case_id,'mode':mode,'stage':stage,'benchmark_call':len(attempts)+1})[0]
            attempt=dict(call_number=len(attempts)+1,reservation=reservation,case_id=case_id,mode=mode,stage=stage)
            handle.seek(0,2);handle.write(json.dumps(attempt)+'\n');handle.flush();os.fsync(handle.fileno())
            raw,trace=client.call(messages,schema,stage,reservation)
            folder=JOURNAL.with_suffix('.responses');folder.mkdir(exist_ok=True)
            with (folder/(reservation+'.json')).open('x') as saved:
                json.dump(dict(**attempt,response=raw,trace=trace),saved,ensure_ascii=True)
                saved.flush();os.fsync(saved.fileno())
            return raw,trace
        except client.ModelFailure as exc:
            stop()
            raise EvaluationError('Challenge provider failure; scope stopped; no retry.') from None
        except Exception:
            stop()
            raise EvaluationError('Current25 provider failure; scope stopped; diagnostics preserved; no retry.') from None
