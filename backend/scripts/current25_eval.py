"""Current 25-document study: validate, prepare, plan or report locally.

Historical run_eval.py remains the historical-v3 runner. No old receipt admits
this new dataset or changed baseline. Live execution needs a new bounded scope.
"""
import argparse
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'backend'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--plan', action='store_true')
    action.add_argument('--prepare-only', action='store_true')
    action.add_argument('--report', action='store_true')
    action.add_argument('--live', action='store_true')
    parser.add_argument('--privacy', action='store_true', help='Prepare or inspect the separate five-test-per-document suite')
    args = parser.parse_args(argv)
    from app.evaluation.simple_config import load_config, EvaluationError
    from app.evaluation.suite_context import current_suite
    from app.evaluation import simple_runner as runner
    from scripts.build_current25 import validate
    from scripts.run_eval import _lock
    try:
        from app.core.environment import load_environment
        load_environment()
        if args.live and args.privacy:
            raise EvaluationError('This authorization covers the 47-case main study only, not privacy execution.')
        counts = validate()
        config = load_config()
        with current_suite():
            data, manifest_sha = runner._manifest()
            output = ROOT/'results/current25'
            if args.live:
                from app.evaluation import current25_scope as scope
                scope.validate(config)
                if os.getenv('LIVE_EVALUATION_ENABLED') != 'true' or os.getenv('LIVE_LLM_ENABLED') != 'true':
                    raise EvaluationError('Explicit live evaluation and answering process flags required')
                runner._identity(config, manifest_sha)
                os.environ['EVAL_MODE'] = '1'
                from scripts.run_eval import _run
                from app.evaluation.current25 import refresh_report
                try:
                    result = _run(data, config, manifest_sha, output=output, origin='azure_live_current25_main_v1')
                    scope.CLOSED.touch(exist_ok=False)
                except BaseException:
                    scope.stop()
                    raise
                finally:
                    refresh_report()
            elif args.privacy:
                from app.evaluation.document_suite import build, directory, snapshot
                path = directory()/'manifest.json'
                privacy = build()
                if path.exists():
                    if json.loads(path.read_text()) != privacy:
                        raise EvaluationError('Current privacy suite differs; create a new version rather than overwriting')
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(privacy, indent=2)+'\n')
                view = snapshot()
                result = {k: view[k] for k in ('n_documents','n_cases','planned_rows','recorded_rows','max_provider_calls')}
                result.update(provider_requests_made=0, live_authorized=False)
            elif args.prepare_only:
                from app.evaluation.simple_index import prepare_store
                os.environ['HF_HUB_OFFLINE'] = '1'
                os.environ['TRANSFORMERS_OFFLINE'] = '1'
                with _lock(runner.store_path()/'operation.lock'):
                    if (runner.store_path()/'identity.json').exists():
                        identity = runner._identity(config, manifest_sha)
                        result = dict(index='existing verified identity preserved', **identity, provider_requests_made=0)
                    else:
                        if any((output/name).exists() for name in ('records.csv','run_metadata.json','attempts.jsonl','retrieval')):
                            raise EvaluationError('Existing observations prevent building a replacement index')
                        result = prepare_store(data, config, runner.store_path(), dataset=runner.dataset_path(),
                                               progress=lambda message: print(message, flush=True))
            elif args.report:
                from app.evaluation.current25 import refresh_report
                result = refresh_report()
            else:
                result = dict(**counts, dataset_version=data['dataset_version'],
                              planned_rows=len(data['cases'])*3,
                              provider_calls_upper_bound=len(data['cases'])*4,
                              reservation_units_upper_bound=len(data['cases'])*4*32000,
                              model=config['model'], settings=config,
                              live_authorized=False, retries=0, fallback=False,
                              expiry=None, results='results/current25',
                              notes='Plan only. Reuses existing aggregate trial capacity only after a new bounded authorization. No results transferred from historical v3.')
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc)+'\n')

if __name__ == '__main__':
    sys.exit(main())
