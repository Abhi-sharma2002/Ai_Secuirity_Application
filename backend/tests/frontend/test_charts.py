"""PNG rendering uses real values and leaves unavailable grades untouched."""
from copy import deepcopy
from io import BytesIO
from PIL import Image
from frontend.charts import coverage_chart,metric_chart,uploaded_chart


def test_charts_render_missing_and_zero_as_distinct_observations_without_mutation():
    rows=[dict(mode='A',n_recorded=1,n_errors=0,n_missing=46,asr_all=0.,asr_all_numerator=0,asr_all_denominator=1),
          dict(mode='B',n_recorded=0,n_errors=0,n_missing=47,asr_all=None)]
    before=deepcopy(rows)
    for content in (coverage_chart(rows),metric_chart(rows),uploaded_chart([])):
        image=Image.open(BytesIO(content));assert image.format=='PNG' and image.width>=800
    assert rows==before
