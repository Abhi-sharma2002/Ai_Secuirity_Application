"""Local reporting for the current study, separate from historical observations."""
from app.evaluation.simple_config import ROOT
from app.evaluation.suite_context import current_suite


def refresh_report():
    from app.evaluation.simple_reporting import make_report
    with current_suite():
        folder = ROOT/'results/current25'
        make_report(folder/'records.csv', folder)
        from app.evaluation.simple_reporting import read_records, manifest, write_csv
        from app.evaluation.case_audit import write_case_audit
        from app.evaluation.simple_review import prepare
        data = manifest()
        rows = read_records(folder/'records.csv', data)
        prepare(folder/'records.csv', folder)
        write_case_audit(folder, folder/'records.csv', rows, data)
        fields = ['case_id', 'query', 'fixtures', 'adversarial', 'channel', 'subtype',
                  'expected_behavior', 'expected_task', 'attack_objective', 'human_review_required']
        import json
        write_csv(folder/'test_cases.csv', fields, [
            {k: json.dumps(c[k]) if isinstance(c.get(k), list) else c.get(k) for k in fields}
            for c in data['cases']])
        from app.evaluation.simple_dashboard import snapshot
        view = snapshot()
        return dict(status=view['status'], counts=view['counts'], provider_requests_made=0)


def snapshot():
    from app.evaluation.simple_dashboard import snapshot as read
    with current_suite():
        return read()
