from copy import deepcopy
import pytest
from frontend.presentation import answer_view,comparison_view
from frontend.observations import observation_metrics

@pytest.mark.parametrize('mode',['A','B','C'])
def test_insufficient_evidence_hides_unrelated_quotes_and_citations_without_rewriting_record(mode):
    raw={'mode':mode,'status':'insufficient_evidence','answer':'Unrelated personal introduction quoted here.',
         'references':[{'id':'chunk','filename':'intro.txt','text':'Unrelated personal introduction.'}],
         'citation_check':'IDs validated; semantic support requires review'}
    before=deepcopy(raw)
    view=answer_view(raw)
    assert view['answer']=='The requested information was not found in the supplied document passages.'
    assert view['references']==[] and raw==before
    assert comparison_view({'results':{mode:raw}})['results'][mode]==view
    metrics={r['Measure']:r['Value'] for r in observation_metrics(raw)}
    assert metrics['Supporting references']=='0'
    assert metrics['Citation ID check']=='N/A — no supported answer'

def test_supported_answer_keeps_its_reference():
    raw={'status':'answered','answer':'Three days.','references':[{'filename':'policy.txt','page':1}]}
    assert answer_view(raw)['answer']=='Three days.'
    assert answer_view(raw)['references']==raw['references']
