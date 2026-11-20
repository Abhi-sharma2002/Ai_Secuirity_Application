# Exact-template presentation review

## Deliverables

- Project-root `AI_Security_Defense_Evaluation_Presentation.pptx`.
- Project-root PDF rendered from that actual PPTX using LibreOffice Impress.
- `Speaker_Notes.md`: readable copy of the updated notes embedded in all ten slides.
- `Slide_Overview.png` and `previews/`: actual rendered slide images.
- `Validation.json`: reproducible structural, data and rendering checks.
- `backup/ForecastIQ_V2_Presentation.original.pptx`: unchanged original backup.

## Reference and assignment

The supplied ForecastIQ deck contains **10 slides**, not eight. Its existing
10-slide order has been preserved. The five-page `Abhishek Sharma.pdf` assignment
requires evaluation of attack resistance alongside task preservation, a synthetic
dataset, a baseline and two defensive configurations, repeatable evaluation,
five metrics, findings, limitations and a representative demo. Those requirements
control content priorities; the reference deck controls design only.

## Project inspection

Repository: `/home/sigmoid/Ai-Security-Poc`.

Inspected project documentation: README.md; docs/architecture.md;
docs/architecture/RUNTIME_MAP.md; docs/ACTIVE_RUNTIME_IMPLEMENTATION.md;
docs/PROJECT_SCOPE.md; docs/REPORT.md; docs/LEARNING_GUIDE.md;
docs/ASSIGNMENT_TRACEABILITY.md; backend/tests/README.md.

Implementation inspected: backend/app/rag/assistant.py and retrieval.py;
backend/app/api/runtime.py; ingestion/lifecycle.py and parsers.py;
defenses/baseline.py, instruction_separation.py, screening.py and
output_screening.py; llm/client.py and azure_openai.py; evaluation/simple_runner.py,
simple_scoring.py, simple_reporting.py and simple_review.py;
backend/scripts/run_eval.py; eval_config.yaml; frontend/streamlit_app.py.
Related indexing/embedding and registry behavior was checked against the active
runtime mapping and source inspected during this project session.

Inspected tests: defenses/test_phase7_separation.py;
evaluation/test_simple_scoring.py; evaluation/test_simple_reporting.py.
Tests demonstrate implementation/control-flow properties, not live effectiveness.

Evaluation evidence: backend/benchmark_v3/manifest.json; results/records.csv;
results/summary.csv; results/spot_check.csv; results/run_metadata.json;
results/document_privacy/*.json; docs/DOCUMENT_PRIVACY_RUN_STATUS.md.
Main metrics were independently recomputed with the current reporting functions
and matched the saved summary. No model calls or benchmark executions occurred.

Some documentation retains historical provider selections and older runner maps.
The active main v3 path uses scripts/run_eval.py and evaluation/simple_runner.py,
not the old benchmark/experiment framework. The older backend/benchmark and
backend/data/test_cases datasets, archived implementations and duplicate nested
repository were not treated as the active main benchmark.

## Architecture verified

Streamlit -> local FastAPI -> source selection / local retrieval -> shared
assistant.respond -> A/B/C -> authorized Azure gpt-5-mini -> response-schema and
citation-ID checks -> local outcomes, human review and metric aggregation.
Parsing, CPU MiniLM embeddings, Chroma retrieval, SQLite registry and evaluation
remain local. Predefined and uploaded sources use separate indexes. Expected
answers and evaluator gold labels are not supplied as answering-model answer keys.

A uses grounding. B adds instruction separation while preserving original chunks.
C adds LLM question/source screening, retains unflagged evidence, uses B answering,
and applies a deterministic payment-card output-pattern check. C is not a general
secret detector. The UI's masking is not scored as model resistance.

## Slide-by-slide changes

1. Original title layout -> project title, PoC focus and verified presenter name.
2. Original overview/bullets/two cards -> application and controlled benchmark.
3. Original objectives/two columns/four counters -> security/evaluation goals and
   verified dataset/configuration/metric counts.
4. Original nine stack tiles -> actual local runtime and evaluation stack.
5. Original architecture-picture location -> updated AI Security layered diagram
   retaining the original image dimensions and arrangement; caption updated.
6. Original eight-stage workflow/five cards -> actual RAG/defense flow and five
   implemented metrics; scoring and fairness notes added in existing boxes.
7. Original three-column cards -> A/B/C mechanisms, implementation and limits.
8. Original six-card grid -> five recorded metrics plus coverage/limitations.
9. Original conclusion bullets -> evidence-based findings and next steps.
10. Original closing layout -> closing text preserved; technical notes updated.

All ten speaker-note bodies were replaced with project-specific explanations,
source references and accurate technical questions/answers. No extra slides.

## Design preservation

The PPTX was edited as an OOXML package derived directly from the supplied file;
it was not recreated using a new theme or generic slide layouts. Validation
compared original and edited slide XML after removing only text-node values.
All slide and notes design XML matched. Slide order, dimensions, shape count,
shape coordinates, paragraphs, run formatting, sizes, fonts, alignment, spacing,
colors, backgrounds, arrows and relationships remain preserved. Masters, layouts
and theme are byte-identical. Corporate logos and decorative elements remain.

The original architecture is a single raster image. That image was replaced in
the unchanged picture shape with a code-drawn diagram using the original layered
arrangement, node placements, palette and arrow style. It remains a raster picture,
as in the template. Three technology-specific icon assets were replaced with
corresponding generic icons at their original dimensions: UI, database and layers.
No new chart objects or unrelated visual design were introduced.

## Evaluation limitations retained

- Main benchmark: 45 sources; 47 cases; 141 recorded rows, including 13 errors.
- ASR: A 2/18, B 0/19, C 0/20 on eligible graded adversarial subsets.
- Benign task success: 20/20 in each eligible mode subset.
- C false positives: 0/20 eligible benign cases; A/B not applicable.
- Only four actual human quality ratings; eleven pending judgments.
- C blocked all twenty graded attack rows and completed zero legitimate tasks in
  that subset. Different eligible subsets prevent a clean universal ranking.
- Separate privacy suite: 92/675 recorded, three errors, 583 unrun at build time.
- Historical prompt/implementation continuations and scoring amendments remain
  relevant. Current summary-v7 rules are not validated by historical ASR figures.
- Keyword/marker grading has semantic limits; unrun, failed or unreviewed rows
  are not security successes. Provider refusal is separate from application block.

## Rendering and unresolved issues

Actual PPTX rendered with LibreOffice Impress, and all ten slide images inspected.
Full-size checks covered dense slides 6, 7 and 8. Every nontrivial native text
paragraph was present in the rendered PDF; no text visibility discrepancies were
found. No unresolved clipping or overlapping text was observed. The architecture
retains the reference's dense image layout and small labels; detailed explanation
is provided in its notes. Office installations can substitute fonts, but no source
font sizes or run formats were changed. The PDF provides a fixed visual copy.

No application source code was modified to create this presentation. No private
settings, keys, endpoints or raw provider payloads were included. The source deck
and its backup have identical SHA-256 hashes.
