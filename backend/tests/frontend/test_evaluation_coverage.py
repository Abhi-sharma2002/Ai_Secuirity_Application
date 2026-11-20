from frontend.evaluation_coverage import attack_coverage,benign_control_blocking
from app.evaluation.simple_dashboard import snapshot
from app.evaluation.document_suite import snapshot as privacy_snapshot


def test_historical_denominators_explain_same_26_attacks_per_mode():
    rows=attack_coverage(snapshot())
    assert [r['Same scheduled attacks'] for r in rows]==[26,26,26]
    assert [r['Errors excluded'] for r in rows]==[4,4,5]
    assert [r['Pending excluded'] for r in rows]==[4,3,1]
    assert [r['ASR denominator'] for r in rows]==[18,19,20]
    assert all(r['Other ungraded']==0 for r in rows)


def test_automatic_control_blocking_excludes_errors_unrun_and_attack_sources():
    result=benign_control_blocking(privacy_snapshot())
    assert result['numerator']==result['denominator']==4 and result['rate']==1
    assert result['errors_excluded']==1 and result['unrun_excluded']==14
    assert result['missing_screening_excluded']==0


def test_no_control_observations_means_unavailable_not_zero():
    assert benign_control_blocking({'documents':[]})['rate'] is None
